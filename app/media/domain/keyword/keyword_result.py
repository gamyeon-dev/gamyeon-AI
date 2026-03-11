from __future__ import annotations
from dataclasses import dataclass

from .value_objects import KeywordCandidate

@dataclass(frozen=True)
class KeywordResult:
    """
    키워드 추출 완료 상태 — Aggregate Root

    candidates: 
    - list → tuple 자동 변환
    - 상위 10개, 추출 실패 시 빈 tuple
    - 파이프라인은 계속 진행 (FAILED 전환 없음)
    """
    candidates: tuple[KeywordCandidate, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, 'candidates', tuple(self.candidates))

    @property
    def is_empty(self) -> bool:
        return len(self.candidates) == 0