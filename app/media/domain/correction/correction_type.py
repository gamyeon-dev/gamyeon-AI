"""LLM CoT 교정 관련 도메인 열거형."""
from enum import Enum

class CorrectionType(str, Enum):
    """
    교정 유형 식별자.

    PHONETIC: Step 1 — 음성 유사 오인식 교정 (문맥 기반)
    TERM: Step 2 — 기술 용어 한영 혼용 교정 (Few-shot)

    MVP2 활용 : corrections[].type == PHONETIC 필터링 -> STT 엔진 인식률 측정, 오차 패턴 분석 활용 가능
    """
    PHONETIC = "phonetic"
    TERM     = "term"