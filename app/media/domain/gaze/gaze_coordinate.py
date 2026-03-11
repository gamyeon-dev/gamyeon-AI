from __future__ import annotations
from dataclasses import dataclass

from .._shared.normalizer import r3

@dataclass(frozen=True)
class GazeCoordinate:
    """
    단일 눈 시선 좌표 - Value Object
    x, y: 화면 기준 정규화 좌표
    """
    x: float
    y: float

    def __post_init__(self) -> None:
        object.__setattr__(self, 'x', r3(self.x))
        object.__setattr__(self, 'y', r3(self.y))