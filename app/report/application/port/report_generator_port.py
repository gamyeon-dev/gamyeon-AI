from abc import ABC, abstractmethod
from app.report.domain.report_model import ReportResult
from app.report.schema.request import FeedbackItem


class ReportGeneratorPort(ABC):
    """
    report feature는 LLM 호출이 없는 완전 정적 처리
    단일 메서드 generate()로 전체 리포트 생성
    저장은 Spring 담당 (ReportRepositoryPort 불필요)
    """
    @abstractmethod
    def generate(
        self,
        feedbacks: list[FeedbackItem],
        intv_id: int  # MetaInfo 제거 — Request에서 직접 전달
    ) -> ReportResult:
        ...
