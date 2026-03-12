from abc import ABC, abstractmethod
from report.domain.report_model import ReportResult, FeedbackItem, MetaInfo

class ReportGeneratorPort(ABC):
    @abstractmethod
    def generate(
        self,
        feedbacks: list[FeedbackItem],
        meta: MetaInfo,
        interview_id: int
    ) -> ReportResult:
        ...
        
""" 
port는 단일 메서드 generate() 하나입니다. report feature는 LLM 호출이 없는 완전 정적 처리이므로 
별도의 ReportRepositoryPort는 불필요합니다 (저장은 Spring 담당).
"""