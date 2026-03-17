"""
ScoringConfigPort 구현체

Consul KV 기반 점수 산출 정책 조회
TTL 60초 캐시로 Consul 부하 방지
Consul 장애 시 캐시 → ScoringConfig 기본값 순서로 fallback
예외 미전파

Consul KV 구조:
- Key: ai-server/scoring/{interview_type}
- Value (JSON):
{
    "limitMs": 60000,
    "reliability": {
        "questionSuccessRateWeight": 50,
        "segmentCoverageWeight":     30,
        "avgWordConfidenceWeight":   20
    }
}
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from core.consul_helper import ConsulHelper
from media.application.port.scoring_config_port import ScoringConfigPort
from media.domain import ScoringConfig

logger = logging.getLogger(__name__)

_CACHE_TTL_SECONDS = 60
_CONSUL_KEY_PREFIX = "ai-server/scoring"


@dataclass
class _CacheEntry:
    config:     ScoringConfig
    expires_at: float


class ConsulScoringConfigAdapter(ScoringConfigPort):
    """
    ConsulHelper 기반 ScoringConfigPort 구현체.

    캐시 전략:
    - TTL 60초 — 만료 전까지 Consul 미호출.
    - Consul 장애 시: 만료 캐시라도 사용 (경고 로그) -> 캐시도 없으면 ScoringConfig 기본값.
    """

    def __init__(self, consul_helper: ConsulHelper) -> None:
        """
        Args:
            consul_helper: core/consul_helper.py ConsulHelper 인스턴스 -> DI에서 주입.
        """
        self._consul  = consul_helper
        self._cache: dict[str, _CacheEntry] = {}

    async def get_config(
        self,
        interview_type: str = "default",
    ) -> ScoringConfig:
        """
        ScoringConfigPort.get_config() 구현.

        조회 순서:
        1. TTL 유효 캐시 → 즉시 반환
        2. Consul KV 조회 → 캐시 갱신 후 반환
        3. Consul 장애 → 만료 캐시 반환 (경고 로그)
        4. 캐시도 없음 → ScoringConfig 기본값 반환
        """
        # 1. TTL 유효 캐시 확인
        cached = self._cache.get(interview_type)
        if cached and time.monotonic() < cached.expires_at:
            return cached.config

        # 2. Consul KV 조회
        try:
            config = self._fetch_from_consul(interview_type)
            self._cache[interview_type] = _CacheEntry(
                config=    config,
                expires_at=time.monotonic() + _CACHE_TTL_SECONDS,
            )
            logger.info(
                "ScoringConfig Consul 조회 성공 type=%s limit_ms=%d",
                interview_type, config.limit_ms,
            )
            return config

        except Exception as e:
            # 3. 장애 시 만료 캐시 사용
            if cached:
                logger.warning(
                    "Consul 장애 — 만료 캐시 사용 type=%s error=%s",
                    interview_type, e,
                )
                return cached.config

            # 4. 캐시도 없으면 기본값
            logger.warning(
                "Consul 장애 + 캐시 없음 — 기본값 사용 type=%s error=%s",
                interview_type, e,
            )
            return ScoringConfig()

    # Private
    def _fetch_from_consul(self, interview_type: str) -> ScoringConfig:
        """
        ConsulHelper.get_config()로 KV 조회.

        Key: ai-server/scoring/{interview_type}
        빈 딕셔너리 반환 시 (키 없음) → 기본값 ScoringConfig 생성
        필수 키 누락 시 → KeyError → 호출자에서 fallback 처리
        """
        key  = f"{_CONSUL_KEY_PREFIX}/{interview_type}"
        data = self._consul.get_config(key)

        if not data:
            logger.warning(
                "Consul KV 값 없음 key=%s — 기본값 사용", key,
            )
            return ScoringConfig()

        return ScoringConfig(
            limit_ms=                    data["limitMs"],
            question_success_rate_weight=data["reliability"]["questionSuccessRateWeight"],
            segment_coverage_weight=     data["reliability"]["segmentCoverageWeight"],
            avg_word_confidence_weight=  data["reliability"]["avgWordConfidenceWeight"],
        )