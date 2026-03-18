"""
media.domain 외부 노출 단일 진입점
내부 BC 폴더 구조를 외부에 노출하지 않음

사용 예:
- from app.media.domain import STTResult, GazeResult, MediaProcessingResult
"""

# STT BC
# Correction BC
from .correction import CorrectionEntry, CorrectionResult, CorrectionType

# Gaze BC
from .gaze import (
    GazeCoordinate,
    GazeDirection,
    GazeEvent,
    GazeEventType,
    GazeMetricsSummary,
    GazeRawFrame,
    GazeResult,
    GazeSegment,
    GazeSegmentMeta,
    GazeSummary,
    GazeVector,
    HeadPose,
)

# Keyword BC
from .keyword import KeywordCandidate, KeywordResult

# Pipeline BC
from .pipeline import MediaProcessingResult

# Scoring BC
from .scoring import (
    ReliabilityFactors,
    ReliabilityGrade,
    ScoringConfig,
    TimeScore,
    reliability,
)
from .stt import STTModelType, STTResult, WordTimestamp

# Transcript BC
from .transcript import TranscriptState

__all__ = [
    # STT
    "STTModelType",
    "WordTimestamp",
    "STTResult",
    # Correction
    "CorrectionType",
    "CorrectionEntry",
    "CorrectionResult",
    # Transcript
    "TranscriptState",
    # Gaze
    "GazeEventType",
    "GazeDirection",
    "GazeCoordinate",
    "GazeVector",
    "HeadPose",
    "GazeRawFrame",
    "GazeEvent",
    "GazeMetricsSummary",
    "GazeSegmentMeta",
    "GazeSummary",
    "GazeSegment",
    "GazeResult",
    # Keyword
    "KeywordCandidate",
    "KeywordResult",
    # Scoring
    "ReliabilityGrade",
    "ScoringConfig",
    "TimeScore",
    "ReliabilityFactors",
    "reliability",
    # Pipeline
    "MediaProcessingResult",
]
