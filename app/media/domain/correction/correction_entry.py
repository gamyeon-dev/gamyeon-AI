"""
S5 LLM CoT 교정 Value Objects
frozen=True: 교정 기록은 생성 후 불변
"""
from __future__ import annotations
from dataclasses import dataclass

from .._shared.normalizer import r2
from .correction_type import CorrectionType


@dataclass(frozen=True)
class CorrectionEntry:
    """
    단일 교정 기록 — Value Object.

    LLM CoT 통합 교정 결과 두 유형 모두 표현:
    - PHONETIC(Step 1): 음성 유사 오인식 교정
    - TERM(Step 2):     기술 용어 한영 교정

    position:   corrected_transcript 기준 문자 오프셋
    confidence: LLM 교정 확신도 (0.0~1.0)
    type:       교정 타입(MVP2 기준)(기본값 TERM)

    MVP1: corrections[] 전체 JSONB 저장
    MVP2: type 필드로 PHONETIC / TERM 분류 집계
    """
    original:   str
    corrected:  str
    position:   int
    confidence: float
    type:       CorrectionType = CorrectionType.TERM

    def __post_init__(self) -> None:
        object.__setattr__(self, 'confidence', r2(self.confidence))