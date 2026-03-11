"""
STT Aggregate Root
"""
from __future__ import annotations
from dataclasses import dataclass

from .._shared.normalizer import r3
from .stt_model_type import STTModelType
from .word_timestamp import WordTimestamp


@dataclass(frozen=True)
class STTResult:
    """
    TT의 결과물 데이터(오인식, 기술 용어 교전 정) - Aggregate Root

    language_porbability
    1. 0.5: 낮은 신뢰도(STT)로 경로 로그 기록, 전체 rebability 패널티
    2. 1의 상태로 Pipeline 계속 진행

    STT Model 사용
    - large_v3: 정상 처리
    - medlum: OOM fallback 발생 -> defraded 패널티 없음, 단순 기록
    """
    raw_transcript:       str
    word_timestamps:      tuple[WordTimestamp, ...]
    language_probability: float
    stt_model_used:       STTModelType

    def __post_init__(self) -> None:
        object.__setattr__(self,
            'word_timestamps',
            tuple(self.word_timestamps),
        )
        object.__setattr__(self,
            'language_probability',
            r3(self.language_probability),
        )

    @property
    def is_low_confidence(self) -> bool:
        """language_probability < 0.5 → 신뢰도 경고 대상."""
        return self.language_probability < 0.5

    @property
    def avg_word_confidence(self) -> float:
        """
        S8 reliability_score 산출 입력값.
        집계 연산 결과 → r3() 적용.
        word_timestamps 없을 경우 0.0 반환.
        """
        if not self.word_timestamps:
            return 0.0
        avg = sum(w.probability for w in self.word_timestamps) / len(self.word_timestamps)
        return r3(avg)