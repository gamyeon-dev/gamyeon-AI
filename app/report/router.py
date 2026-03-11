from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException

from app.report.application.service import ReportService
from app.report.infrastructure.di import get_report_service
from app.report.schema.request import ReportRequest
from app.report.schema.response import ReportResponse


# convention: /[prefix]/[version]/[domain]/[action]
# → POST /internal/v1/report/generate
router = APIRouter(prefix="/internal/v1/report", tags=["report"])


@router.post("/generate")
def generate_report(
    request: ReportRequest,
    service: ReportService = Depends(get_report_service),
):
    try:
        result = service.execute(request)
    except ValueError as e:
        # 성공 피드백 2개 이하 등 비즈니스 에러
        # 공통 포맷을 detail에 실어 전달 → Spring이 그대로 사용
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "code": "RPRT_001",
                "message": str(e),
                "data": None,
            },
        )

    # domain(dataclass) → dict → Pydantic 모델로 변환
    response_data = ReportResponse.model_validate(asdict(result))

    return {
        "success": True,
        "code": "S000",
        "message": "success",
        "data": response_data,
    }
