"""
Media 모듈 FastAPI 의존성 주입 설정

헥사고날 원칙:
- service.py는 포트 인터페이스만 의존
- DI에서 구현체를 포트에 바인딩
- 구현체 교체 시 이 파일만 수정

싱글턴 전략:
- 모델 로드 비용이 큰 어댑터 (Whisper, Okt)는
- 애플리케이션 시작 시 1회만 생성
- FastAPI lifespan 또는 lru_cache 활용
"""
from __future__ import annotations

from functools import lru_cache
from fastapi import Depends

from core.config import settings
from media.application.service                        import MediaService
from media.application.service_helper.gaze_aggregator import GazeAggregator
from media.infrastructure.whisper_stt_adapter          import WhisperSTTAdapter
from media.infrastructure.claude_haiku_adapter         import ClaudeHaikuAdapter
from media.infrastructure.inmemory_gaze_buffer         import InMemoryGazeBuffer
from media.infrastructure.consul_scoring_config        import ConsulScoringConfigAdapter
from media.infrastructure.keyword_extractor_impl       import KeywordExtractorImpl

# 싱글턴 어댑터 (애플리케이션 생명주기와 동일)
@lru_cache(maxsize=1)
def _get_whisper_adapter() -> WhisperSTTAdapter:
    """
    Whisper 모델 어댑터 싱글턴
    lru_cache로 애플리케이션 당 1회만 생성
    모델 lazy load는 어댑터 내부에서 처리
    """
    return WhisperSTTAdapter(
        device=settings.WHISPER_DEVICE,
        compute_type=settings.WHISPER_COMPUTE_TYPE,
    )


@lru_cache(maxsize=1)
def _get_claude_adapter() -> ClaudeHaikuAdapter:
    return ClaudeHaikuAdapter(
        api_key=settings.ANTHROPIC_API_KEY,
        model=settings.CLAUDE_HAIKU_MODEL,
        timeout=settings.LLM_TIMEOUT_SECONDS,
    )


@lru_cache(maxsize=1)
def _get_gaze_buffer() -> InMemoryGazeBuffer:
    """
    인메모리 Gaze 버퍼 싱글턴.
    MVP-2: RedisGazeBuffer로 교체 시 이 함수만 수정.
    """
    return InMemoryGazeBuffer()


@lru_cache(maxsize=1)
def _get_consul_adapter() -> ConsulScoringConfigAdapter:
    return ConsulScoringConfigAdapter(
        consul_url=settings.CONSUL_URL,
        token=settings.CONSUL_TOKEN,
    )


@lru_cache(maxsize=1)
def _get_keyword_extractor() -> KeywordExtractorImpl:
    """konlpy Okt 싱글턴 (초기 로드 비용 절감)."""
    return KeywordExtractorImpl()


@lru_cache(maxsize=1)
def _get_gaze_aggregator() -> GazeAggregator:
    return GazeAggregator()

# FastAPI Depends 진입점
def get_media_service(
    stt_port=         Depends(_get_whisper_adapter),
    correction_port=  Depends(_get_claude_adapter),
    gaze_buffer=      Depends(_get_gaze_buffer),
    scoring_config=   Depends(_get_consul_adapter),
    keyword_extractor=Depends(_get_keyword_extractor),
    gaze_aggregator=  Depends(_get_gaze_aggregator),
) -> MediaService:
    """
    MediaService FastAPI 의존성

    router.py 사용 예:
    @router.post("/internal/media/process")
    async def process(
        service: MediaService = Depends(get_media_service),
    ): ...
    """
    return MediaService(
        stt_port=          stt_port,
        correction_port=   correction_port,
        gaze_buffer=       gaze_buffer,
        scoring_config=    scoring_config,
        keyword_extractor= keyword_extractor,
        gaze_aggregator=   gaze_aggregator,
    )