"""
STT + 교정 파이프라인 완료 후 트랜스크립트 집계 - Value Object
키워드 추출 + Gaze 교차 매핑

하위 VO 참조:
- WordTimestamp
- CorrectionEntry
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .._shared.normalizer import r3
from ..stt.stt_model_type import STTModelType
from ..stt.word_timestamp import WordTimestamp
from ..correction.correction_entry import CorrectionEntry

@dataclass(frozen=True)
class TranscriptState:
    """
    STT + LLM 교정 전 단계 집계 상태 — Value Object

    raw_transcript:
    - Whisper 원본
    - 재분석 및 파이프라인 재처리 기준점

    corrected_transcript:
    - LLM CoT 교정 완료 텍스트
    - 키워드 추출 입력값
    - feedback 모듈 평가 입력값

    word_timestamps:
    - raw 기준 오프셋 (초 단위)
    - Gaze 교차 매핑 기준점

    phonetic_corrected:
    - STT 중간 결과.
    - feedback 이벤트 페이로드 전용
    - Degraded 시 None

    degraded:
    - S5 LLM 교정 실패 시 True
    - corrected_transcript == raw_transcript 로 대체
    """
    raw_transcript:       str
    corrected_transcript: str
    word_timestamps:      tuple[WordTimestamp, ...]
    corrections:          tuple[CorrectionEntry, ...]
    language_probability: float
    stt_model_used:       STTModelType
    phonetic_corrected:   Optional[str] = None
    degraded:             bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self,
            'word_timestamps',
            tuple(self.word_timestamps),
        )
        object.__setattr__(self,
            'corrections',
            tuple(self.corrections),
        )
        object.__setattr__(self,
            'language_probability',
            r3(self.language_probability),
        )