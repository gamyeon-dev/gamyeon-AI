# app/report/router.py webhook
from fastapi import APIRouter, BackgroundTasks, Depends

from app.report.application.service import ReportService
from app.report.infrastructure.di import get_report_service
from app.report.schema.request import ReportGenerateRequest

router = APIRouter(prefix="/internal/v1/reports", tags=["report"])


@router.post("/generate", status_code=202)
async def generate_report(
    request: ReportGenerateRequest,
    background_tasks: BackgroundTasks,
    service: ReportService = Depends(get_report_service),
):
    """
    Spring → AI 리포트 생성 요청
    - 즉시 202 Accepted 반환
    - 리포트 생성 및 콜백 전송은 BackgroundTasks로 비동기 처리
    """
    background_tasks.add_task(service.execute_and_callback, request)

    return {
        "success": True,
        "code": "S000",
        "message": "accepted",
        "data": None,
    }
