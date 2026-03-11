from functools import lru_cache

from app.report.application.service import ReportService
from app.report.infrastructure.static_score_adapter import StaticScoreAdapter


@lru_cache
def get_report_service() -> ReportService:
    adapter = StaticScoreAdapter()
    return ReportService(adapter=adapter)
