from datetime import datetime, timezone
from app.report.application.port.report_generator_port import ReportGeneratorPort
from app.report.application.port.callback_port import CallbackPort
from app.report.infrastructure.static_score_adapter import StaticScoreAdapter
from app.report.schema.request import ReportGenerateRequest, FeedbackStatus
from app.report.schema.response import ReportCallbackPayload, CallbackStatus
from app.report.domain.report_model import (
    CompetencyScores, QuestionFeedbackDetail, QuestionSummary, ReportResult
)


class ReportService:

    def __init__(self, adapter: StaticScoreAdapter):
        self.adapter = adapter

    def execute(self, request: ReportGenerateRequest) -> ReportResult:
        # 1. SUCCEED 항목만 필터링
        completed = [f for f in request.feedbacks if f.status == FeedbackStatus.SUCCEED]
        success_count = len(completed)

        # 2. 성공 개수 검증 (2개 이하 → 호출부에서 422 처리)
        if success_count <= 2:
            raise ValueError(f"리포트 생성 불가: 성공한 피드백이 {success_count}개입니다.")

        # 단일 generate() 호출로 전체 리포트 생성
        result = self.adapter.generate(feedbacks=completed, intv_id=request.intv_id)
        return result
    # ── 웹훅 전송 포함 실행 (BackgroundTasks 진입점) ─────────

    async def execute_and_callback(self, request: ReportGenerateRequest) -> None:
        """
        리포트 생성 후 결과를 Spring 서버에 콜백 전송.
        성공/실패 모두 콜백을 보장 (finally 미사용, 명시적 분기).
        """
        try:
            result = self.execute(request)
            payload = ReportCallbackPayload.from_result(
                intv_id=request.intv_id,
                user_id=request.user_id,
                result=result,
            )
        except Exception as e:
            payload = ReportCallbackPayload.failed(
                intv_id=request.intv_id,
                user_id=request.user_id,
                error_message=str(e),
            )

        await self.callback_port.send(
            url=request.callback,
            payload=payload,
        )