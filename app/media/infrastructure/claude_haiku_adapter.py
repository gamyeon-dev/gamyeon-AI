"""
S5 TranscriptCorrectionPort 구현체

Claude Haiku 3.5 선택 이유:
    ① 속도: Sonnet 대비 3~4배 빠름 -> STT 직후 연속 호출 → 지연 최소화 필요
    ② 비용: Sonnet 대비 약 10배 저렴 -> 질문당 1회 호출 → 누적 비용 중요
    ③ 품질: 교정 태스크는 창의성 불필요 -> 구조화된 JSON 출력 + Few-shot → Haiku로 충분
    ④ 컨텍스트: 면접 답변 평균 200~500 토큰 -> Haiku 컨텍스트 윈도우 내 충분히 처리 가능

프롬프트 파일:
- prompts/correction/correction.yaml  시스템 프롬프트 + human 템플릿 + tech_hint
- prompts/correction/few_shot.json    Few-shot 예시

Degraded Mode:
- JSON 파싱 실패 / timeout / API 오류 → 예외 미전파
- degraded=True CorrectionResult 반환
"""
from __future__ import annotations

import json, logging
from pathlib import Path
from typing import Any

import yaml
import anthropic

from media.application.port.transcript_correction_port import TranscriptCorrectionPort
from media.domain.correction.correction_result         import CorrectionResult
from media.domain.correction.correction_entry          import CorrectionEntry
from media.domain.correction.correction_type           import CorrectionType

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent /"prompts"/"correction"

class ClaudeHaikuAdapter(TranscriptCorrectionPort):
    """
    Claude Haiku 3.5 TranscriptCorrectionPort 구현체

    초기화 시 프롬프트 파일 1회 로드:
    - correction.yaml → system_prompt, human_prompt, tech_hint
    - few_shot.json   → few_shot 예시 목록
    """

    def __init__(
        self,
        api_key: str,
        model: str   = "claude-haiku-4-5-20251001",
        timeout: float = 15.0,
    ) -> None:
        self._client  = anthropic.Anthropic(api_key=api_key)
        self._model   = model
        self._timeout = timeout

        # 프롬프트 로드 (correction.yaml)
        with open(_PROMPT_DIR / "correction.yaml", encoding = "utf-8") as f :
            prompt = yaml.safe_load(f)

        self._system_prompt = prompt["system_prompt"]
        self._human_prompt  = prompt["human_prompt"]
        self._tech_hint     = prompt["tech_hint"]

        # few-shot.json 로드
        with open(_PROMPT_DIR / "few_shot.json", encoding = "utf-8") as f :
            self._few_shot: list[dict] = json.load(f)

        logger.info(
            "[MEDIA]ClaudeHaikuAdapter 초기화 완료 model=%s few_shot=%d개",
            self._model, len(self._few_shot),
        )

    async def correct(
        self,
        raw_transcript: str,
        tech_stack: list[str],
    ) -> CorrectionResult:
        """
        TranscriptCorrectionPort.correct() 구현
        실패 시 Degraded CorrectionResult 반환 (예외 미전파)
        """
        try:
            raw_json = await self._call_llm(raw_transcript, tech_stack)
            return self._parse_response(raw_json, raw_transcript)

        except Exception as e:
            logger.warning("[MEDIA - CLAUDE_HAIKU]LLM 교정 실패 — Degraded 전환: %s", e)
            return self._degraded_result(raw_transcript)


    # Private
    async def _call_llm(
        self,
        raw_transcript: str,
        tech_stack: list[str],
    ) -> CorrectionResult :
        """
        Claude API 호출
        JSON 파싱 실패 시 1회 재시도 (JSON only 강조 추가)
        """
        user_content = self._build_user_prompt(raw_transcript, tech_stack)

        for attempt in range(2) :
            try:
                response = self._client.messages.create(
                    model=self._model,
                    max_tokens=1000,
                    system=(
                        self._system_prompt if attempt == 0
                        else self._system_prompt + "\n반드시 JSON만 반환하세요."
                    ),
                    messages=[{"role": "user", "content": user_content}],
                    timeout=self._timeout,
                )
                return json.loads(response.content[0].text.strip())

            except json.JSONDecodeError as e :
                if attempt == 0:
                    logger.warning("[MEDIA - CLAUDE_HAIKU]JSON 파싱 실패 — 1회 재시도: %s", e)
                    continue
                raise

        raise RuntimeError("[MEDIA - CLAUDE_HAIKU]JSON 파싱 2회 모두 실패")

    def _build_user_prompt(
        self,
        raw_transcript: str,
        tech_stack: list[str],
    ) -> str:
        """
        human_prompt 템플릿에 값 주입

        few_shot_examples: few_shot.json 기반 입력/출력 쌍 조합

        tech_hint:
        - tech_stack 있음 → with_stack 템플릿
        - tech_stack 없음 → without_stack 텍스트 → 일반 IT 용어 기준 교정 진행.
        """
        return self._human_prompt.format(
            few_shot_example = self._build_few_shot_text(),
            tech_hint = self._build_tech_hint(tech_stack),
            raw_transcript = raw_transcript
        )

    def _build_few_shot_text(self) -> str:
        """
        few_shot.json → 프롬프트 삽입용 텍스트 변환

        형식:
        - 입력: {input}
        - 출력: {output json}
        """
        return "\n".join(
            f"입력: {ex['input']}\n"
            f"출력: {json.dumps({'phonetic_corrected': ex['phonetic_corrected'], 
                            'corrected_transcript': ex['output'], 
                            'corrections': ex['corrections']}, 
                            ensure_ascii=False)}"
            for ex in self._few_shot
        )

    def _build_tech_hint(self, tech_stack: list[str]) -> str:
        """
        tech_stack 유무에 따라 tech_hint 분기

        있음: "techStack: Redis, Docker, Spring Boot"
        없음: "techStack: 정보 없음 → 일반적인 IT 기술 용어 기준으로 교정해 주세요"
        """
        if tech_stack:
            return self._tech_hint["with_stack"].format(
                tech_stack=", ".join(tech_stack)
            )
        return self._tech_hint["without_stack"]

    def _parse_response(
        self,
        data: dict[str, Any],
        raw_transcript: str,
    ) -> CorrectionResult:
        """
        LLM JSON 응답 → CorrectionResult 변환
        필수 필드 누락 / 값 오류 → Degraded 처리
        """
        try:
            entries = tuple(
                CorrectionEntry(
                    original=   c["original"],
                    corrected=  c["corrected"],
                    position=   c["position"],
                    confidence= c["confidence"],
                    type=       CorrectionType(c.get("type", "term")),
                )
                for c in data.get("corrections", [])
            )
            return CorrectionResult(
                corrected_transcript=data["corrected_transcript"],
                corrections=         entries,
                phonetic_corrected=  data.get("phonetic_corrected"),
                degraded=            False,
            )
        
        except (KeyError, ValueError) as e:
            logger.warning("[MEDIA - CLAUDE_HAIKU]응답 파싱 실패 — Degraded 처리: %s", e)
            return self._degraded_result(raw_transcript)

    @staticmethod
    def _degraded_result(raw_transcript: str) -> CorrectionResult:
        """Degraded Mode CorrectionResult 생성."""
        return CorrectionResult(
            corrected_transcript=raw_transcript,
            corrections=         (),
            phonetic_corrected=  None,
            degraded=            True,
        )