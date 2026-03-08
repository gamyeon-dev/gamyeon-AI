from abc import ABC, abstractmethod
from app.question.domain.interview_input import InterviewInput

class StructuringPort(ABC):

    @abstractmethod
    async def structure(
        self,
        resume_text: str,
        job_role: str,
        portfolio_text: str | None = None,
        self_intro_text: str | None = None,
    ) -> InterviewInput:
        pass
