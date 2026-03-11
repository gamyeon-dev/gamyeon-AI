"""
LLM CoT 통합 교정 - Aggregate Root

CoT 내부 처리 순서 (단일 LLM 호출):
1. 음성 유사 오인식 교정 (문맥 기반)
2. 1의 결과 기반 기술 용어 한영 교정 (Few-shot)

phonetic_corrected:
- Step 1 완료 중간 텍스트.
- Webhook 미포함 / feedback 이벤트 전용
- MVP-2 backoffice STT 인식률 분석용
- Degraded 시 None
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .correction_type import CorrectionType
from .correction_entry import CorrectionEntry

@dataclass(frozen=True)
class CorrectionResult:
    """
    LLM CoT 통합 교정 완료 상태 — Aggregate Root

    Degraded Mode 식별:
      degraded = True
      + corrections = ()
      + corrected_transcript == raw_transcript 입력값
      + phonetic_corrected = None

    corrections 빈 tuple:
      정상: 교정 대상 없음 (degraded = False)
      Degraded: 교정 시도 자체 실패 (degraded = True)
      → 반드시 degraded 플래그로 구분.
    """
    corrected_transcript: str
    corrections:          tuple[CorrectionEntry, ...]
    phonetic_corrected:   Optional[str] = None  # MVP-2 STT 분석용
    degraded:             bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self,
            'corrections',
            tuple(self.corrections),
        )

    @property
    def phonetic_correction_count(self) -> int:
        """PHONETIC 유형 교정 건수 — MVP-2 STT 인식률 측정 기준."""
        return sum(1 for c in self.corrections if c.type == CorrectionType.PHONETIC)

    @property
    def term_correction_count(self) -> int:
        """TERM 유형 교정 건수 — MVP-2 기술 용어 혼동 분석 기준."""
        return sum(1 for c in self.corrections if c.type == CorrectionType.TERM)