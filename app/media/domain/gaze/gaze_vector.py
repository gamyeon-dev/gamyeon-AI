"""
좌우 눈 시선 좌표 쌍 Value Objects
"""
from __future__ import annotations
from dataclasses import dataclass

from .gaze_coordinate import GazeCoordinate

@dataclass(frozen=True)
class GazeVector:
    """좌우 눈 시선 좌표 쌍 — Value Object"""
    left:  GazeCoordinate
    right: GazeCoordinate