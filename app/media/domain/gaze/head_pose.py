"""
헤드 포즈 Value Objects
"""
from __future__ import annotations
from dataclasses import dataclass

from .._shared.normalizer import r3

@dataclass(frozen=True)
class HeadPose:
    """
    헤드 포즈 (단위: deg)
    pitch: 상하 회전 (고개 끄덕임)
    yaw:   좌우 회전 (고개 돌림)
    roll:  좌우 기울임
    """
    pitch: float
    yaw:   float
    roll:  float

    def __post_init__(self) -> None:
        object.__setattr__(self, 'pitch', r3(self.pitch))
        object.__setattr__(self, 'yaw',   r3(self.yaw))
        object.__setattr__(self, 'roll',  r3(self.roll))