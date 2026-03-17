from abc import ABC, abstractmethod
from app.question.domain.interview_input import InterviewInput
# 인터뷰 질문 생성 포트 (인터페이스)-delete?
class QuestionGenPort(ABC):

    @abstractmethod
    async def generate(self, interview_input: InterviewInput) -> list[str]:
        """InterviewInput을 기반으로 면접 질문 목록을 생성"""
        pass
