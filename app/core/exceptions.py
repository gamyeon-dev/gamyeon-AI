"""
도메인 전용 예외 클래스

각 예외는 파이프라인 실패 단계를 구분해
usecase 레이어에서 Spring Boot에 정확한 error_code를 전달
"""


class STTTranscriptionError(Exception):
    """Whisper STT 실패 (large-v3 + medium fallback 모두 실패)"""


class MediaDownloadError(Exception):
    """S3 다운로드 실패"""


class MediaValidationError(Exception):
    """포맷/크기 검증 또는 ffprobe 실패"""


class AudioExtractionError(Exception):
    """ffmpeg 오디오 추출 실패"""
