"""
S6 KeywordExtractor 구현체.

형태소 분석 (konlpy) + IT 기술 용어 화이트리스트 매칭.
외부 API 없음 — 순수 CPU 처리.

Phase 3 구현 포인트:
1. konlpy Okt 형태소 분석
2. IT 기술 용어 화이트리스트 매칭(BE / FE / AI / DevOps 카테고리)
3. 출현 횟수 집계 → 상위 10개 반환
"""
from __future__ import annotations

import logging
from collections import Counter

from app.media.application.service_helper.keyword_extractor import KeywordExtractor
from app.media.domain import KeywordResult, KeywordCandidate

logger = logging.getLogger(__name__)

# IT 기술 용어 화이트리스트
# { 용어: 카테고리 }
_WHITELIST: dict[str, str] = {
    # Backend
    "Spring Boot": "BE", "JPA": "BE", "QueryDSL": "BE",
    "Redis": "BE", "MySQL": "BE", "PostgreSQL": "BE",
    "Kafka": "BE", "RabbitMQ": "BE", "REST API": "BE",
    # Frontend
    "React": "FE", "Vue": "FE", "TypeScript": "FE",
    "Next.js": "FE", "Webpack": "FE",
    # AI
    "PyTorch": "AI", "TensorFlow": "AI", "FastAPI": "AI",
    "LangChain": "AI", "Whisper": "AI",
    # DevOps
    "Docker": "DevOps", "Kubernetes": "DevOps",
    "GitHub Actions": "DevOps", "Jenkins": "DevOps",
    "AWS": "DevOps", "Terraform": "DevOps",
}

_MAX_CANDIDATES = 10


class KeywordExtractorImpl(KeywordExtractor):
    """
    konlpy 기반 IT 기술 용어 키워드 추출 구현체.
    """

    def __init__(self) -> None:
        # konlpy lazy import (초기 로드 비용 지연)
        self._okt = None

    async def extract(self, text: str) -> KeywordResult:
        """
        KeywordExtractor.extract() 구현.

        처리 순서:
        1. 형태소 분석 (konlpy Okt)
        2. 화이트리스트 매칭
        3. 출현 횟수 집계 → 상위 10개
        """
        if not text.strip():
            return KeywordResult(candidates=())

        try:
            okt     = self._get_okt()
            tokens  = okt.morphs(text, stem=True)
            counter = Counter(tokens)

            candidates: list[KeywordCandidate] = []
            for term, category in _WHITELIST.items():
                count = self._count_term(term, text, counter)
                if count > 0:
                    candidates.append(
                        KeywordCandidate(
                            term=term,
                            count=count,
                            category=category,
                        )
                    )

            # 출현 횟수 내림차순 정렬 → 상위 10개
            top_candidates = sorted(
                candidates,
                key=lambda c: c.count,
                reverse=True,
            )[:_MAX_CANDIDATES]

            logger.info(
                "키워드 추출 완료 total=%d top=%d",
                len(candidates), len(top_candidates),
            )

            return KeywordResult(candidates=tuple(top_candidates))

        except Exception as e:
            logger.warning("키워드 추출 실패: %s", e)
            raise

    def _get_okt(self):
        """konlpy Okt lazy load"""
        if self._okt is None:
            from konlpy.tag import Okt
            self._okt = Okt()
        return self._okt

    def _count_term(
        self,
        term: str,
        text: str,
        counter: Counter,
    ) -> int:
        """
        복합어 (예: Spring Boot) 는 원문 직접 매칭.
        단일어는 형태소 분석 결과 counter 활용.
        """
        if " " in term:
            return text.lower().count(term.lower())
        return counter.get(term, 0)