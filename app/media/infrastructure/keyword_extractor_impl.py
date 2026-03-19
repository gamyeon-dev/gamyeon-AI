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
    # ── Backend Framework / Library ───────────────────────────────
    "Spring": "BE", "Spring Boot": "BE", "Spring MVC": "BE",
    "Spring Security": "BE", "Spring Data": "BE", "Spring Cloud": "BE",
    "JPA": "BE", "Hibernate": "BE", "QueryDSL": "BE", "MyBatis": "BE",
    "Django": "BE", "Flask": "BE", "FastAPI": "BE", "Express": "BE",
    "NestJS": "BE", "Laravel": "BE", "Ruby on Rails": "BE",
    "gRPC": "BE", "GraphQL": "BE", "REST API": "BE", "RESTful": "BE",
    "WebSocket": "BE", "OAuth": "BE", "JWT": "BE",

    # ── Database ──────────────────────────────────────────────────
    "MySQL": "BE", "PostgreSQL": "BE", "MariaDB": "BE", "Oracle": "BE",
    "MongoDB": "BE", "DynamoDB": "BE", "Cassandra": "BE",
    "Elasticsearch": "BE", "OpenSearch": "BE",
    "Redis": "BE", "Memcached": "BE",
    "SQLite": "BE", "MSSQL": "BE",

    # ── Message Queue / Event ─────────────────────────────────────
    "Kafka": "BE", "RabbitMQ": "BE", "SQS": "BE", "ActiveMQ": "BE",
    "Pub/Sub": "BE", "이벤트 드리븐": "BE", "Event Driven": "BE",
    "MSA": "BE", "마이크로서비스": "BE", "Microservice": "BE",

    # ── Architecture / Design Pattern ────────────────────────────
    "MVC": "BE", "MVP": "BE", "MVVM": "BE",
    "DDD": "BE", "TDD": "BE", "BDD": "BE",
    "OOP": "BE", "객체지향": "BE", "함수형": "BE",
    "헥사고날": "BE", "클린 아키텍처": "BE", "Clean Architecture": "BE",
    "SOLID": "BE", "디자인 패턴": "BE", "Design Pattern": "BE",
    "싱글톤": "BE", "팩토리": "BE", "옵저버": "BE", "전략 패턴": "BE",
    "캐싱": "BE", "Caching": "BE", "인덱스": "BE", "Index": "BE",
    "트랜잭션": "BE", "Transaction": "BE", "동시성": "BE", "Concurrency": "BE",
    "비동기": "BE", "Async": "BE", "멀티스레드": "BE", "멀티쓰레드": "BE",

    # ── Frontend ──────────────────────────────────────────────────
    "React": "FE", "Vue": "FE", "Angular": "FE", "Svelte": "FE",
    "Next.js": "FE", "Nuxt.js": "FE", "Gatsby": "FE",
    "TypeScript": "FE", "JavaScript": "FE",
    "HTML": "FE", "CSS": "FE", "Sass": "FE", "Tailwind": "FE",
    "Webpack": "FE", "Vite": "FE", "Babel": "FE",
    "Redux": "FE", "Zustand": "FE", "Recoil": "FE",
    "TanStack Query": "FE", "React Query": "FE", "SWR": "FE",
    "SSR": "FE", "CSR": "FE", "SPA": "FE",

    # ── AI / ML ───────────────────────────────────────────────────
    "PyTorch": "AI", "TensorFlow": "AI", "Keras": "AI",
    "LangChain": "AI", "Whisper": "AI", "GPT": "AI",
    "LLM": "AI", "RAG": "AI", "Fine-tuning": "AI", "파인튜닝": "AI",
    "머신러닝": "AI", "딥러닝": "AI", "Machine Learning": "AI", "Deep Learning": "AI",
    "자연어처리": "AI", "NLP": "AI", "컴퓨터비전": "AI", "Computer Vision": "AI",
    "Scikit-learn": "AI", "Pandas": "AI", "NumPy": "AI",
    "Hugging Face": "AI", "OpenAI": "AI", "벡터 DB": "AI", "Vector DB": "AI",

    # ── DevOps / Infra ────────────────────────────────────────────
    "Docker": "DevOps", "Kubernetes": "DevOps", "k8s": "DevOps",
    "GitHub Actions": "DevOps", "Jenkins": "DevOps", "GitLab CI": "DevOps",
    "CircleCI": "DevOps", "ArgoCD": "DevOps",
    "AWS": "DevOps", "GCP": "DevOps", "Azure": "DevOps", "Naver Cloud": "DevOps",
    "EC2": "DevOps", "S3": "DevOps", "Lambda": "DevOps", "EKS": "DevOps",
    "Terraform": "DevOps", "Ansible": "DevOps", "Helm": "DevOps",
    "Nginx": "DevOps", "Apache": "DevOps", "Linux": "DevOps",
    "CI/CD": "DevOps", "배포": "DevOps", "모니터링": "DevOps",
    "Prometheus": "DevOps", "Grafana": "DevOps", "ELK": "DevOps",

    # ── Collaboration / Version Control ───────────────────────────
    "Git": "협업", "GitHub": "협업", "GitLab": "협업", "Bitbucket": "협업",
    "Jira": "협업", "Confluence": "협업", "Notion": "협업",
    "애자일": "협업", "스크럼": "협업", "Agile": "협업", "Scrum": "협업",
    "코드 리뷰": "협업", "Code Review": "협업",

    # ── 한글 alias (STT가 한글로 전사한 경우) ────────────────────
    "스프링": "BE", "스프링부트": "BE", "제이피에이": "BE",
    "리액트": "FE", "뷰": "FE", "타입스크립트": "FE", "자바스크립트": "FE",
    "도커": "DevOps", "쿠버네티스": "DevOps", "젠킨스": "DevOps",
    "카프카": "BE", "레디스": "BE", "마이에스큐엘": "BE",
    "깃허브": "협업", "깃": "협업", "깃랩": "협업",
    "지피티": "AI", "엘엘엠": "AI",
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
            logger.warning("키워드 추출 입력 텍스트 비어있음")
            return KeywordResult(candidates=())

        logger.info("키워드 추출 시작 text_length=%d text_preview=%s", len(text), text[:80])

        # 형태소 분석 (konlpy 없으면 빈 counter로 fallback)
        counter: Counter = Counter()
        try:
            okt    = self._get_okt()
            tokens = okt.morphs(text, stem=True)
            counter = Counter(tokens)
            logger.debug("형태소 분석 결과 token_count=%d tokens=%s", len(tokens), tokens[:20])
        except Exception as e:
            logger.warning("형태소 분석 실패 — 원문 직접 매칭으로 진행: %s", e)

        try:
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
                "키워드 추출 완료 total=%d top=%d terms=%s",
                len(candidates), len(top_candidates),
                [c.term for c in top_candidates],
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
        단일어는 형태소 counter + 원문 직접 매칭 병행 (둘 중 큰 값).
        """
        if " " in term:
            return text.lower().count(term.lower())
        return max(counter.get(term, 0), text.lower().count(term.lower()))