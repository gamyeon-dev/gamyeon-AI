from __future__ import annotations
from dataclasses import dataclass

from .gaze_event_type import GazeEventType
from .gaze_direction import GazeDirection

@dataclass(frozen=True)
class GazeEvent:
    """
    시선 이탈 이벤트 — Value Object
    AWAY_START / AWAY_END 쌍으로 이탈 구간 계산
    offset_ms: 세그먼트 시작 기준 오프셋 (ms), 정수형
    direction: 이탈 방향 (AWAY_START 시점 기준)
    """
    type:      GazeEventType
    offset_ms: int
    direction: GazeDirection