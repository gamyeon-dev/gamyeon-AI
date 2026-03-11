"""
STT 단어 수준 타임 스탬프 Value Object
"""
from __future__ import annotations
from dataclasses import dataclass

from .._shared.normalizer import r2, r3

@dataclass(frozen=True)
class WordTimestamp:
    """
    단어 수준 타임스탬프 — word_timestamps=True 옵션 결과.

    start / end: 답변 시작 기준 오프셋 (초)
    probability: Whisper 토큰 단위 confidence (0.0~1.0)

    S7 Gaze 집계에서 이벤트 + 단어 교차 매핑에 사용
    reliability_score 산출 시 평균 답변(단어 기반) 신뢰도 계산 기준이 됨
    """
    word:        str
    start:       float
    end:         float
    probability: float

    def __post_init__(self) -> None :
        self.start = r3(self.start)
        self.end - r3(self.end)
        self.probability = r2(self.probability)