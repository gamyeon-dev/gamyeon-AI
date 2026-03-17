"""
media.domain 외부 노출 단일 진입점
내부 BC 폴더 구조를 외부에 노출하지 않음

사용 예:
- from app.media.domain import STTResult, GazeResult, MediaProcessingResult
"""

# STT BC
from .stt        import STTModelType, WordTimestamp, STTResult
# Correction BC
from .correction import CorrectionType, CorrectionEntry, CorrectionResult
# Transcript BC
from .transcript import TranscriptState
# Gaze BC
from .gaze       import (
    GazeEventType, GazeDirection,
    GazeCoordinate, GazeVector, HeadPose,
    GazeRawFrame, GazeEvent,
    GazeMetricsSummary, GazeSegmentMeta, GazeSummary,
    GazeSegment, GazeResult,
)
# Keyword BC
from .keyword    import KeywordCandidate, KeywordResult
# Scoring BC
from .scoring    import (
    ReliabilityGrade,
    ScoringConfig, TimeScore, ReliabilityFactors,
    ReliabilityScore,
)
# Pipeline BC
from .pipeline   import MediaProcessingResult

__all__ = [
    # STT
    "STTModelType", "WordTimestamp", "STTResult",
    # Correction
    "CorrectionType", "CorrectionEntry", "CorrectionResult",
    # Transcript
    "TranscriptState",
    # Gaze
    "GazeEventType", "GazeDirection",
    "GazeCoordinate", "GazeVector", "HeadPose",
    "GazeRawFrame", "GazeEvent",
    "GazeMetricsSummary", "GazeSegmentMeta", "GazeSummary",
    "GazeSegment", "GazeResult",
    # Keyword
    "KeywordCandidate", "KeywordResult",
    # Scoring
    "ReliabilityGrade",
    "ScoringConfig", "TimeScore", "ReliabilityFactors",
    "ReliabilityScore",
    # Pipeline
    "MediaProcessingResult",
]