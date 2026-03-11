"""
media 모듈 아웃바운드 포트 진입점.

포트 목록:
STTPort                  ← S4 STT 엔진 추상화
TranscriptCorrectionPort ← S5 LLM CoT 교정 추상화
GazeBufferPort           ← Gaze 세그먼트 큐 추상화
ScoringConfigPort        ← Consul KV 정책 조회 추상화
"""

from .stt_port            import STTPort, TranscriptCorrectionPort
from .gaze_buffer_port    import GazeBufferPort
from .scoring_config_port import ScoringConfigPort

__all__ = [
    "STTPort",
    "TranscriptCorrectionPort",
    "GazeBufferPort",
    "ScoringConfigPort",
]