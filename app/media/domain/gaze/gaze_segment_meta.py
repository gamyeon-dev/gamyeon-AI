from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class GazeSegmentMeta:
    """
    세그먼트 식별 정보 — Value Object
    segment_sequence: 버퍼 정렬 기준
    timestamp: 세그먼트 시작 epoch ms
    """
    interview_id:     int
    question_id:      int
    timestamp:        int
    segment_sequence: int