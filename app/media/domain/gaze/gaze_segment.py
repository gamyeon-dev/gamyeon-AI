from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .gaze_event_type import GazeEventType
from .gaze_segment_meta import GazeSegmentMeta
from .gaze_metrics_summary import GazeMetricsSummary
from .gaze_raw_frame import GazeRawFrame
from .gaze_event import GazeEvent

@dataclass(frozen=True)
class GazeSegment:
    """
    10초 단위 Gaze 세그먼트 — Sub-Aggregate

    raw_data, events: list → tuple 자동 변환
    버퍼 정렬 기준: meta.segment_sequence 오름차순
    raw_data[] 전체 적재
    """
    meta:            GazeSegmentMeta
    metrics_summary: GazeMetricsSummary
    raw_data:        tuple[GazeRawFrame, ...]
    events:          tuple[GazeEvent, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, 'raw_data', tuple(self.raw_data))
        object.__setattr__(self, 'events',   tuple(self.events))

    @property
    def away_duration_ms(self) -> int:
        """
        AWAY_START / AWAY_END 쌍으로 이탈 총 시간 산출
        세그먼트 경계에서 잘린 미완성 쌍은 무시
        """
        total:    int = 0
        start_ms: Optional[int] = None

        for event in sorted(self.events, key=lambda e: e.offset_ms):
            if event.type == GazeEventType.AWAY_START:
                start_ms = event.offset_ms
            elif event.type == GazeEventType.AWAY_END and start_ms is not None:
                total   += event.offset_ms - start_ms
                start_ms = None

        return total

    @property
    def away_count(self) -> int:
        """AWAY_START 이벤트 수 = 이탈 횟수"""
        return sum(1 for e in self.events if e.type == GazeEventType.AWAY_START)