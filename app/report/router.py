from fastapi import APIRouter, Depends, HTTPException

from app.report.application.service import ReportService
from app.report.infrastructure.di import get_report_service
from app.report.schema.request import ReportRequest
from app.report.schema.response import ReportResponse

router = APIRouter(prefix="/api/ai/report", tags=["report"])


@router.post("/generate", response_model=ReportResponse)
def generate_report(
    request: ReportRequest,
    service: ReportService = Depends(get_report_service),
) -> ReportResponse:
    try:
        result = service.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return ReportResponse(
        interview_id=result.interview_id,
        job_category=result.job_category,
        answered_count=result.answered_count,
        avg_answer_duration_ms=result.avg_answer_duration_ms,
        created_at=result.created_at,
        report_accuracy=result.report_accuracy,
        competency_scores=result.competency_scores,
        total_score=result.total_score,
        strengths=result.strengths,
        weaknesses=result.weaknesses,
        question_summaries=result.question_summaries,
    )
