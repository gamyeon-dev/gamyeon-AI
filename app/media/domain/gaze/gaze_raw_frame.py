from __future__ import annotations
from dataclasses import dataclass

from .._shared.normalizer import r2

from .gaze_vector import GazeVector
from .head_pose import HeadPose

@dataclass(frozen=True)
class GazeRawFrame:
    """
    프레임 단위 원시 데이터 — Value Object

    offset_ms:  세그먼트 시작 기준 오프셋 (ms)
    confidence: 시선 추적 신뢰도 (0.0~1.0)

    S7 word_timestamps 교차 매핑:
    - frame.offset_ms(ms) / 1000 → word.start(초) 단위 변환
    """
    offset_ms:  int
    confidence: float
    gaze:       GazeVector
    head:       HeadPose

    def __post_init__(self) -> None:
        object.__setattr__(self, 'confidence', r2(self.confidence))