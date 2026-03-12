from __future__ import annotations

import logging
from dataclasses import dataclass

from media.domain import (
    STTResult,          # STT
    CorrectionResult,   # Correction
    TranscriptState,    # Transcript
    GazeResult,         # Gaze
    KeywordResult,      # Keyword
    ScoringConfig, TimeScore, ReliabilityFactors, ReliabilityScore, # Scoring
    MediaProcessingResult, # Pipeline
)
from media.application.port.stt_port            import STTPort, TranscriptCorrectionPort
from media.application.port.gaze_buffer_port    import GazeBufferPort
from media.application.port.scoring_config_port import ScoringConfigPort
from media.application.service_helper.keyword_extractor  import KeywordExtractor
from media.application.service_helper.gaze_aggregator    import GazeAggregator
from core.exceptions import STTTranscriptionError

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# 서비스 입력 커맨드 (Inbound DTO 대신 순수 도메인 커맨드)
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class ProcessMediaCommand:
    """
    POST /internal/media/process 수신 데이터를
    서비스 레이어로 전달하는 커맨드 객체.

    router.py에서 schema → command 변환 후 service 호출.
    service.py는 schema에 직접 의존하지 않음 (헥사고날 원칙).
    """
    job_id:             str
    interview_id:       str
    question_id:        str
    audio_path:         str          # /tmp/{jobId}/audio.wav
    answer_duration_ms: int
    tech_stack:         tuple[str, ...]
    interview_type:     str = "default"  # Consul KV 분기 (MVP-2)


# ──────────────────────────────────────────────
# 메인 서비스
# ──────────────────────────────────────────────

class MediaService:
    """
    Media 파이프라인 오케스트레이터.

    포트 주입:
    - stt_port:         STTPort
    - correction_port:  TranscriptCorrectionPort
    - gaze_buffer:      GazeBufferPort
    - scoring_config:   ScoringConfigPort

    도메인 서비스 주입:
    - keyword_extractor: KeywordExtractor (CPU 기반, 외부 API 없음)
    - gaze_aggregator:   GazeAggregator   (순수 계산, 외부 API 없음)
    """

    def __init__(
        self,
        stt_port:          STTPort,
        correction_port:   TranscriptCorrectionPort,
        gaze_buffer:       GazeBufferPort,
        scoring_config:    ScoringConfigPort,
        keyword_extractor: KeywordExtractor,
        gaze_aggregator:   GazeAggregator,
    ) -> None:
        self._stt          = stt_port
        self._correction   = correction_port
        self._gaze_buffer  = gaze_buffer
        self._scoring      = scoring_config
        self._keywords     = keyword_extractor
        self._gaze_agg     = gaze_aggregator

    # ──────────────────────────────────────────
    # Public: 파이프라인 진입점
    # ──────────────────────────────────────────

    async def process(
        self,
        command: ProcessMediaCommand,
    ) -> MediaProcessingResult:
        """
        파이프라인 실행 후 MediaProcessingResult 반환.

        STTTranscriptionError 발생 시에만 FAILED.
        나머지 단계 실패는 Degraded 처리 후 계속 진행.

        Raises:
            STTTranscriptionError: 실패 시 router.py에서 FAILED 페이로드 전송.
        """
        logger.info(
            "파이프라인 시작 job_id=%s question_id=%s",
            command.job_id, command.question_id,
        )

        # S4: STT
        stt_result = await self._run_stt(command)

        # S5: LLM CoT 교정
        correction_result = await self._run_correction(stt_result, command)

        # TranscriptState 조립
        transcript = self._build_transcript(stt_result, correction_result)

        # S6 + S7: fan-out 병렬 실행
        import asyncio
        keyword_result, gaze_result = await asyncio.gather(
            self._run_keyword_extraction(transcript),
            self._run_gaze_aggregation(command),
        )

        # S8: 점수 산출
        config = await self._scoring.get_config(command.interview_type)
        time_score, reliability_score = self._run_scoring(
            stt_result=stt_result,
            gaze_result=gaze_result,
            answer_duration_ms=command.answer_duration_ms,
            config=config,
        )

        # 최종 집계
        degraded = (
            transcript.degraded      # S5 실패
            or gaze_result.is_empty  # S7 Gaze 미수신
            or keyword_result.is_empty  # S6 추출 실패
        )

        result = MediaProcessingResult(
            job_id=command.job_id,
            interview_id=command.interview_id,
            question_id=command.question_id,
            transcript=transcript,
            keywords=keyword_result,
            gaze=gaze_result,
            time=time_score,
            reliability=reliability_score,
            degraded=degraded,
        )

        logger.info(
            "파이프라인 완료 job_id=%s degraded=%s",
            command.job_id, degraded,
        )

        return result

    async def buffer_gaze_segment(self, segment) -> None:
        """
        POST /internal/media/gaze/segment 수신 시 호출.
        GazeBufferPort에 위임.
        """
        await self._gaze_buffer.push(segment)

    # ──────────────────────────────────────────
    # Private: 단계별 실행 메서드
    # ──────────────────────────────────────────

    async def _run_stt(
        self,
        command: ProcessMediaCommand,
    ) -> STTResult:
        """
        Whisper STT
        실패 시 STTTranscriptionError → 파이프라인 FAILED
        language_probability < 0.5 → 경고 로그 + 처리 계속
        """
        result = await self._stt.transcribe(
            audio_path=command.audio_path,
            tech_stack=list(command.tech_stack),
        )

        if result.is_low_confidence:
            logger.warning(
                "STT 신뢰도 낮음 job_id=%s language_probability=%.3f",
                command.job_id,
                result.language_probability,
            )

        logger.info(
            "STT 완료 job_id=%s model=%s words=%d",
            command.job_id,
            result.stt_model_used.value,
            len(result.word_timestamps),
        )

        return result

    async def _run_correction(
        self,
        stt_result: STTResult,
        command: ProcessMediaCommand,
    ) -> CorrectionResult:
        """
        S5: LLM CoT 통합 교정
        실패 시 Degraded Mode 자동 강등 (예외 미전파)
        """
        result = await self._correction.correct(
            raw_transcript=stt_result.raw_transcript,
            tech_stack=list(command.tech_stack),
        )

        if result.degraded:
            logger.warning(
                "LLM 교정 Degraded job_id=%s",
                command.job_id,
            )
        else:
            logger.info(
                "LLM 교정 완료 job_id=%s phonetic=%d term=%d",
                command.job_id,
                result.phonetic_correction_count,
                result.term_correction_count,
            )

        return result

    def _build_transcript(
        self,
        stt_result: STTResult,
        correction_result: CorrectionResult,
    ) -> TranscriptState:
        """
        S4 + S5 결과를 TranscriptState VO로 조립
        두 AR의 값을 읽기만 하고 새 불변 객체 생성
        """
        return TranscriptState(
            raw_transcript=stt_result.raw_transcript,
            corrected_transcript=correction_result.corrected_transcript,
            word_timestamps=stt_result.word_timestamps,
            corrections=correction_result.corrections,
            language_probability=stt_result.language_probability,
            stt_model_used=stt_result.stt_model_used,
            phonetic_corrected=correction_result.phonetic_corrected,
            degraded=correction_result.degraded,
        )

    async def _run_keyword_extraction(
        self,
        transcript: TranscriptState,
    ) -> KeywordResult:
        """
        S6: 키워드 추출 (CPU, 외부 API 없음)
        실패 시 빈 tuple 반환, 파이프라인 계속 진행
        """
        try:
            result = await self._keywords.extract(
                text=transcript.corrected_transcript,
            )
            logger.info(
                "키워드 추출 완료 candidates=%d",
                len(result.candidates),
            )
            return result
        except Exception as e:
            logger.warning("키워드 추출 실패 — 빈 결과 반환: %s", e)
            return KeywordResult(candidates=())

    async def _run_gaze_aggregation(
        self,
        command: ProcessMediaCommand,
    ) -> GazeResult:
        """
        S7: Gaze 집계.
        버퍼에서 pop_all() 후 GazeAggregator에 위임
        세그먼트 0개 → is_empty=True → Degraded 판단.
        """
        segments = await self._gaze_buffer.pop_all(command.question_id)

        if not segments:
            logger.warning(
                "Gaze 세그먼트 없음 question_id=%s",
                command.question_id,
            )

        result = self._gaze_agg.aggregate(
            segments=segments,
            answer_duration_ms=command.answer_duration_ms,
        )

        logger.info(
            "Gaze 집계 완료 gaze_score=%s coverage=%.3f",
            result.gaze_score,
            result.summary.segment_coverage,
        )

        return result

    def _run_scoring(
        self,
        stt_result: STTResult,
        gaze_result: GazeResult,
        answer_duration_ms: int,
        config: ScoringConfig,
    ) -> tuple[TimeScore, ReliabilityScore]:
        """
        S8: 시간 점수 + 신뢰도 점수 산출.
        Consul KV 정책(ScoringConfig) 기반.
        도메인 calculate() 직접 호출.
        """
        time_score = TimeScore.calculate(
            answer_duration_ms=answer_duration_ms,
            config=config,
        )

        factors = ReliabilityFactors(
            question_success_rate=1.0,
            segment_coverage=gaze_result.summary.segment_coverage,
            avg_word_confidence=stt_result.avg_word_confidence,
        )
        reliability_score = ReliabilityScore.calculate(
            factors=factors,
            config=config,
        )

        logger.info(
            "점수 산출 완료 time=%d reliability=%d grade=%s",
            time_score.time_score,
            reliability_score.score,
            reliability_score.grade.value,
        )

        return time_score, reliability_score