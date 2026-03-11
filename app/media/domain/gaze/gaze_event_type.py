from enum import Enum

class GazeEventType(str, Enum):
    """
    시선 이탈 이벤트 유형
    AWAY_START / AWAY_END 쌍으로 이탈 구간 및 duration 계산
    """
    AWAY_START = "AWAY_START"
    AWAY_END   = "AWAY_END"