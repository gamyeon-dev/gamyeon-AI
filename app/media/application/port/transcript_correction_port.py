from __future__ import annotations

from abc import ABC, abstractmethod

from app.media.domain import CorrectionResult

class TranscriptCorrectionPort(ABC):
    """
    LLM CoT 통합 교정 아웃바운드 포트

    책임:
    - raw_transcript → CorrectionResult 변환
    - CoT 내부 처리 순서 (단일 LLM 호출):
        Step 1: 음성 유사 오인식 교정 (문맥 기반)
                예) "데이터네이스" → "데이터베이스"
        Step 2: Step 1 결과 기반 기술 용어 한영 교정 (Few-shot)
                예) "레디스" → "Redis"

    Degraded Mode 정책:
    - JSON 파싱 실패 / timeout / API 오류 → 예외 미전파.
    - 어댑터 내부에서 degraded=True CorrectionResult 반환.
    - service.py는 FAILED 처리 없이 degraded 플래그만 전파.

    구현체: infrastructure/claude_haiku_adapter.py
    """

    @abstractmethod
    async def correct(
        self,
        raw_transcript: str,
        tech_stack:     list[str],
    ) -> CorrectionResult:
        """
        음성 오인식 교정 + 기술 용어 교정 통합 수행.

        Args:
            raw_transcript: S4 Whisper 원본 텍스트
            tech_stack:     Few-shot 도메인 분류 + 컨텍스트 힌트

        Returns:
            CorrectionResult:
            - 정상    → corrected_transcript + corrections[] + degraded=False
                        phonetic_corrected: Step 1 중간 결과 포함
            - Degraded → raw_transcript 원본 + corrections=() + degraded=True
                        phonetic_corrected=None

        Raises:
            없음. 모든 실패는 어댑터 내부에서 Degraded Mode 처리.
        """
        ...