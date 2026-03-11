from __future__ import annotations
from dataclasses import dataclass

from .._shared.normalizer import r2, r3

@dataclass(frozen=True)
class GazeSummary:
    """
    전체 답변 구간 Gaze 집계 요약 — Value Object
    pop_all() 후 GazeAggregator에서 생성

    avg_concentration: 전체 세그먼트 가중 평균
    segment_coverage:  수신 세그먼트 수 ÷ 예상 세그먼트 수
    avg_confidence:    전체 프레임 평균 신뢰도
    """
    avg_concentration: float
    away_count:        int
    away_total_ms:     int
    segment_coverage:  float
    avg_confidence:    float

    def __post_init__(self) -> None:
        object.__setattr__(self,
            'avg_concentration',
            r3(self.avg_concentration),
        )
        object.__setattr__(self,
            'segment_coverage',
            r3(self.segment_coverage),
        )
        object.__setattr__(self,
            'avg_confidence',
            r2(self.avg_confidence),
        )