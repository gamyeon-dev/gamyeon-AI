from abc import ABC, abstractmethod
from app.feedback.domain.feedback_model import QuestionFeedback
from app.feedback.schema.request import FeedbackRequest


class FeedbackPort(ABC):

    @abstractmethod
    async def generate_feedback(self, request: FeedbackRequest) -> QuestionFeedback:
        """
        입력된 문항과 답변을 평가하여 QuestionFeedback 도메인 모델을 반환합니다.
        SKIPPED / FAILED 처리 포함. 예외를 외부로 전파하지 않습니다.
        """
        ...
