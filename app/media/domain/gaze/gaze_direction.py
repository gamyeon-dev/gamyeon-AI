from enum import Enum

class GazeDirection(str, Enum):
    """
    시선 이탈 방향 — AWAY_START 시점 기준
    MVP2 방향별 이탈 패턴 분석 기준
    """
    CENTER       = "CENTER"
    LEFT         = "LEFT"
    RIGHT        = "RIGHT"
    TOP          = "TOP"
    BOTTOM       = "BOTTOM"
    TOP_LEFT     = "TOP-LEFT"
    TOP_RIGHT    = "TOP-RIGHT"
    BOTTOM_LEFT  = "BOTTOM-LEFT"
    BOTTOM_RIGHT = "BOTTOM-RIGHT"