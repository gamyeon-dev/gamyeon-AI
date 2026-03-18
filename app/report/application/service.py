import json

from app.core.config import settings
from app.report.application.port.callback_port import CallbackPort
from app.report.application.port.report_generator_port import ReportGeneratorPort
from app.report.domain.report_model import ReportResult
from app.report.schema.request import FeedbackStatus, ReportGenerateRequest
from app.report.schema.response import ReportCallbackPayload


class ReportService:
    # 1. 생성자에서 callback_port를 추가로 받도록 수정
    def __init__(
        self,
        adapter: ReportGeneratorPort,  # 구체 클래스(StaticScoreAdapter) 대신 Port
        callback_port: CallbackPort,
    ):
        self.adapter = adapter
        self.callback_port = callback_port

    def execute(self, request: ReportGenerateRequest) -> ReportResult:
        # 1. SUCCEED 항목만 필터링
        completed = [f for f in request.feedbacks if f.status == FeedbackStatus.SUCCEED]
        success_count = len(completed)

        # 2. 성공 개수 검증 (2개 이하 → 호출부에서 422 처리)
        if success_count <= 2:
            raise ValueError(
                f"리포트 생성 불가: 성공한 피드백이 {success_count}개입니다."
            )

        # 단일 generate() 호출로 전체 리포트 생성
        result = self.adapter.generate(
            feedbacks=completed,
            intv_id=request.intv_id,
        )
        return result

    # ── 웹훅 전송 포함 실행 (BackgroundTasks 진입점) ─────────
    async def execute_and_callback(self, request: ReportGenerateRequest) -> None:
        # 1. 초기값 설정 (변수명 통일: payload_obj)
        payload_obj = ReportCallbackPayload.failed(
            intv_id=request.intv_id,
            user_id=request.user_id,
            error_message="알 수 없는 시스템 에러가 발생했습니다.",
        )

        try:
            result = self.execute(request)

            payload_obj = ReportCallbackPayload.from_result(
                intv_id=request.intv_id,
                user_id=request.user_id,
                result=result,
            )

            print(f"✅ 리포트 생성 성공! (intvId: {request.intv_id})")

            # 🔍 로그 출력 시 by_alias=True를 넣어야 카멜케이스가 보입니다!
            final_json = payload_obj.model_dump(mode="json", by_alias=True)
            print("📋 [전송 데이터 요약]:")
            print(json.dumps(final_json, indent=2, ensure_ascii=False))

        except Exception as e:
            print(f"❌ 리포트 생성 중 에러 발생: {str(e)}")

            payload_obj = ReportCallbackPayload.failed(
                intv_id=request.intv_id,
                user_id=request.user_id,
                error_message=str(e),
            )

        # 🚀 [중요] try-except 문 밖으로 완전히 빼내야 성공/실패 모두 전송됩니다!
        if payload_obj is not None:
            print(f"📤 콜백 전송 시도 중... URL: {settings.REPORT_SPRING_WEBHOOK_URL}")

            await self.callback_port.send(
                url=settings.REPORT_SPRING_WEBHOOK_URL,
                payload=payload_obj,  # Adapter에서 model_dump(by_alias=True)가 실행됨
            )
