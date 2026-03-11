from __future__ import annotations
from dataclasses import dataclass

from .._shared.normalizer import r3

@dataclass(frozen=True)
class ReliabilityFactors:
    """
    신뢰도 점수 산출 인자 — Value Object

    question_success_rate: MVP-1 단일 질문 → 1.0 or 0.0.
    segment_coverage:      GazeSummary.segment_coverage 동일값.
    avg_word_confidence:   STTResult.avg_word_confidence 동일값.
    """
    question_success_rate: float
    segment_coverage:      float
    avg_word_confidence:   float

    def __post_init__(self) -> None :
        object.__setattr__(self,
            'question_success_rate',
            r3(self.question_success_rate),
        )
        object.__setattr__(self,
            'segment_coverage',
            r3(self.segment_coverage),
        )
        object.__setattr__(self,
            'avg_word_confidence',
            r3(self.avg_word_confidence),
        )