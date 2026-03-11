from enum import Enum
from typing import Self

class ReliabilityGrade(str, Enum):
    """
    신뢰도 등급
    """
    HIGH =   "높음"
    MEDIUM = "중간"
    LOW =    "낮음"

    @classmethod
    def from_score(cls, score: int) -> Self :
        match score :
            case s if s >= 85: return cls.HIGH
            case s if s >= 60: return cls.MEDIUM
            case _: return cls.LOW