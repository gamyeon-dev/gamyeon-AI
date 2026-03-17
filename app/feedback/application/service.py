import logging
from app.core.config import settings
from app.core.config import settings
from app.feedback.application.port.feedback_port import FeedbackPort
from app.feedback.application.port.callback_port import FeedbackCallbackPort
from app.feedback.domain.feedback_model import QuestionFeedback
from app.feedback.schema.request import FeedbackRequest, FeedbackEventRequest
from app.feedback.schema.response import FeedbackResponse

logger = logging.getLogger(__name__)


class FeedbackService:

    def __init__(self, feedback_port: FeedbackPort, callback: FeedbackCallbackPort) -> None:
        self._port = feedback_port
        self._callback = callback

    async def run(self, event: FeedbackEventRequest) -> None:
        try:
            request = self._to_request(event)          # ← 변환
            result: QuestionFeedback = await self._port.generate_feedback(request)
            payload = self._to_response(event, result)
        except Exception as e:
            payload = FeedbackResponse(
                intv_id          = event.intv_id,
                intv_question_id = event.question_id,
                status           = "FAILED",
                error_message    = str(e),
            )

        await self._callback.send(
            url=settings.FEEDBACK_SPRING_WEBHOOK_URL,
            payload=payload,
        )

    # ── FeedbackEventRequest → FeedbackRequest ───────────────────
    @staticmethod
    def _to_request(event: FeedbackEventRequest) -> FeedbackRequest:
        return FeedbackRequest(
            intv_question_id     = event.question_id,
            question_content        = event.question_content,       # ← 아래 확인
            corrected_transcript = event.transcript.corrected_transcript,
            degraded             = event.degraded,
            reliability_score    = event.reliability.score,
            gaze_score           = event.gaze.gaze_score,
            time_score           = event.time.time_score,
            answer_duration_ms   = event.time.answer_duration_ms,
            keyword_candidates   = event.keywords.candidates,
        )

    # ── QuestionFeedback → FeedbackResponse ─────────────────────
    @staticmethod
    def _to_response(event: FeedbackEventRequest, domain: QuestionFeedback) -> FeedbackResponse:
        return FeedbackResponse(
            intv_id                  = event.intv_id,          # ← 이벤트에서 직접
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
            reliability              = domain.reliability_score,
        )
