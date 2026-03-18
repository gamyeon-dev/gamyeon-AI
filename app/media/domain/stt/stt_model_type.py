"""STT 관련 도메인 열거형."""
from enum import Enum

class STTModelType(str, Enum):
    """
    faster-whisper 모델 식별자
    large-v3 → medium 순서로 OOM fallback 발생 시 추적
    feedback 이벤트 페이로드 sttModelUsed 필드로 전달
    """
    LARGE_V3 = "large-v3"
    MEDIUM   = "medium"
    SMALL    = "small"