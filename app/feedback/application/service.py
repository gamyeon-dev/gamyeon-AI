from app.feedback.application.port.feedback_port import FeedbackPort
from app.feedback.domain.feedback_model import QuestionFeedback
from app.feedback.schema.request import FeedbackRequest
from app.feedback.schema.response import FeedbackResponse


class FeedbackService:

    def __init__(self, feedback_port: FeedbackPort) -> None:
        self._port = feedback_port

    async def generate_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        result: QuestionFeedback = await self._port.generate_feedback(request)
        return self._to_response(result)

    @staticmethod
    def _to_response(domain: QuestionFeedback) -> FeedbackResponse:
        return FeedbackResponse(
            intv_question_id         = domain.intv_question_id,
            status                   = domain.status,
            logic_score              = domain.logic_score,
            answer_composition_score = domain.answer_composition_score,
            characteristic           = domain.characteristic,
            answer_summary           = domain.answer_summary,
            strength                 = domain.strength,
            improvement              = domain.improvement,
            feedback_badges          = domain.feedback_badges,
            gaze_score               = domain.gaze_score,
            time_score               = domain.time_score,
            answer_duration_ms       = domain.answer_duration_ms,
            keyword_count            = domain.keyword_count,
        )
