from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class KeywordCandidate:
    """
    단일 키워드 후보 — Value Object
    term:     추출된 기술 용어
    count:    corrected_transcript 내 출현 횟수
    category: BE, FE, AI, DevOps 화이트리스트 분류
    """
    term:     str
    count:    int
    category: str