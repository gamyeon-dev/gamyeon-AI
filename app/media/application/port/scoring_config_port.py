from abc import ABC, abstractmethod

from media.domain import ScoringConfig


class ScoringConfigPort(ABC) :
    """
    Consul KV 기반 Scoring 정책 조회 추상화 포트.

    포트 추상화 이유:
    - 테스트 환경에서 Consul 없이 LocalScoringConfigAdapter로 대체 가능.
    - Consul 외 다른 설정 저장소로 교체 시 service.py 변경 없음.
    """

    @abstractmethod
    async def get_config(
        self,
        interview_type: str = "default",
    ) -> ScoringConfig :
        """
        Consul KV에서 점수 산출 정책 조회.

        Args:
            interview_type: Consul KV 경로 분기 키.
                            MVP-1: "default" 고정.
                            MVP-2: "tech" | "personality" | "executive"

        Returns:
            ScoringConfig:
            - 정상    → Consul KV 조회값으로 생성된 ScoringConfig
            - 장애    → 캐시 또는 ScoringConfig 기본값 (경고 로그)

        Raises:
            없음. 모든 장애는 내부에서 fallback 처리.
            ScoringConfig 기본값(60s, 50/30/20)이 항상 반환됨.
        """
        ...