from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ScoringConfig:
    """
    Consul KV 조회 점수 산출 정책 — Value Object

    Consul KV 경로:
    - ai-server/scoring/default (MVP-1)
    - ai-server/scoring/{interview_type} (MVP-2)

    Consul 장애 시 기본값 fallback:
    - limit_ms = 60_000
    - 가중치   = 50 / 30 / 20
    """
    limit_ms:                     int   = 60_000
    question_success_rate_weight: float = 50.0
    segment_coverage_weight:      float = 30.0
    avg_word_confidence_weight:   float = 20.0

    def __post_init__(self) -> None:
        total = (
            self.question_success_rate_weight
            + self.segment_coverage_weight
            + self.avg_word_confidence_weight
        )
        if abs(total - 100.0) > 0.01:
            raise ValueError(
                f"ScoringConfig 가중치 합계 오류: {total}"
                " — Consul KV 값 확인 필요"
            )