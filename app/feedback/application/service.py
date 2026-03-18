import logging

from app.core.config import settings
from app.feedback.application.port.callback_port import FeedbackCallbackPort
from app.feedback.application.port.feedback_port import FeedbackPort
from app.feedback.domain.feedback_model import QuestionFeedback
from app.feedback.schema.request import FeedbackEventRequest, FeedbackRequest
from app.feedback.schema.response import FeedbackResponse

logger = logging.getLogger(__name__)


class FeedbackService:

    def __init__(
        self, feedback_port: FeedbackPort, callback: FeedbackCallbackPort
    ) -> None:
        self._port = feedback_port
        self._callback = callback
        # 🚀 1. 이벤트 버스가 호출할 엔트리 포인트 메서드 추가

    async def media_completed(self, payload: dict) -> None:
        """이벤트 버스(blinker)로부터 dict 데이터를 받아 처리 시작"""
        try:
            # dict를 Pydantic 모델로 변환 (유효성 검사 포함)
            event_request = FeedbackEventRequest.model_validate(payload)
            await self.run(event_request)
        except Exception as e:
            logger.error(f"이벤트 데이터 파싱 실패: {e}")

    async def run(self, event: FeedbackEventRequest) -> None:
        try:
            request = self._to_request(event)  # ← 변환
            result: QuestionFeedback = await self._port.generate_feedback(request)
            payload = self._to_response(event, result)
        except Exception as e:
            payload = FeedbackResponse(
                intv_id=event.intv_id,
                intv_question_id=event.question_id,
                status="FAILED",
                error_message=str(e),
                # 필수 필드들은 기본값(0 또는 빈 값)으로 채워야 Pydantic 에러가 나지 않습니다.
                logic_score=0,
                answer_composition_score=0,
                reliability=0,
                characteristic="N/A",
                answer_summary="N/A",
                strength="N/A",
                improvement="N/A",
                feedback_badges=[],
                gaze_score=0,
                time_score=0,
                answer_duration_ms=0,
                keyword_count=0,
            )

        await self._callback.send(
            url=settings.FEEDBACK_SPRING_WEBHOOK_URL,
            payload=payload,
        )

    # ── FeedbackEventRequest → FeedbackRequest ───────────────────
    @staticmethod
    def _to_request(event: FeedbackEventRequest) -> FeedbackRequest:
        return FeedbackRequest(
            intv_question_id=event.question_id,
            question_content=event.question_content,  # ← 아래 확인
            corrected_transcript=event.transcript.corrected_transcript,
            degraded=event.degraded,
            reliability_score=event.reliability.score,
            gaze_score=event.gaze.gaze_score,
            time_score=event.time.time_score,
            answer_duration_ms=event.time.answer_duration_ms,
            keyword_candidates=event.keywords.candidates,
        )

    # ── QuestionFeedback → FeedbackResponse ─────────────────────
    @staticmethod
    def _to_response(
        event: FeedbackEventRequest, domain: QuestionFeedback
    ) -> FeedbackResponse:
        return FeedbackResponse(
            intv_id=event.intv_id,
            intv_question_id=domain.intv_question_id,
            # Enum인 경우 .value를 써서 문자열로 넘겨주는 것이 안전합니다.
            status=(
                domain.status.value
                if hasattr(domain.status, "value")
                else str(domain.status)
            ),
            # 🚀 Optional 필드들에 대해 'or'를 사용하여 None 방지
            logic_score=domain.logic_score or 0,
            answer_composition_score=domain.answer_composition_score or 0,
            characteristic=domain.characteristic or "평가 내용 없음",
            answer_summary=domain.answer_summary or "요약 없음",
            strength=domain.strength or "내용 없음",
            improvement=domain.improvement or "내용 없음",
            feedback_badges=domain.feedback_badges,  # 리스트는 이미 field(default_factory=list)로 안전함
            gaze_score=domain.gaze_score,
            time_score=domain.time_score,
            answer_duration_ms=domain.answer_duration_ms,
            keyword_count=domain.keyword_count,
            reliability=domain.reliability_score,
        )
