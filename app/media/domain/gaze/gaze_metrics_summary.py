from __future__ import annotations
from dataclasses import dataclass

from .._shared.normalizer import r3

@dataclass(frozen=True)
class GazeMetricsSummary:
    """
    세그먼트 단위 집계 지표 — Value Object
    average_concentration: 0.0~1.0 → r3() 적용
    blink_count: 정수형, 정규화 불필요
    """
    average_concentration: float
    blink_count:           int
    is_away_detected:      bool

    def __post_init__(self) -> None:
        object.__setattr__(self,
            'average_concentration',
            r3(self.average_concentration)
        )