from abc import ABC, abstractmethod
from app.question.domain.interview_input import InterviewInput

class QuestionGenPort(ABC):

    @abstractmethod
    async def generate(self, interview_input: InterviewInput) -> list[str]:
        """InterviewInput을 기반으로 면접 질문 목록을 생성"""
        pass
