from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .gaze_summary import GazeSummary
from .gaze_segment import GazeSegment

@dataclass(frozen=True)
class GazeResult:
    """
    Gaze 집계 완료 상태 — Aggregate Root

    gaze_score: 0~100 정수
                세그먼트 미수신 시 None (Degraded)
    segments:   list → tuple 자동 변환
                segmentSequence 오름차순 정렬 완료 상태로 수신
    """
    gaze_score: Optional[int]
    summary:    GazeSummary
    segments:   tuple[GazeSegment, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, 'segments', tuple(self.segments))

    @property
    def is_empty(self) -> bool:
        """세그먼트 미수신 → Degraded Mode 판단 기준"""
        return len(self.segments) == 0