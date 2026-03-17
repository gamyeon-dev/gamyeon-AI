from fastapi import APIRouter, BackgroundTasks, Depends
from app.core.schema import ApiResponse
from app.feedback.application.service import FeedbackService
from app.feedback.infrastructure.di import get_feedback_service
from app.feedback.schema.request import FeedbackEventRequest
from app.feedback.schema.response import FeedbackResponse



router = APIRouter(prefix="/internal/v1/feedbacks", tags=["feedback"])


@router.post("/generate", status_code=202)
async def generate_feedback(
    request: FeedbackEventRequest,
    background_tasks: BackgroundTasks,
    service: FeedbackService = Depends(get_feedback_service),
):
    background_tasks.add_task(service.run, request)
    return {"success": True, "code": "S000", "message": "success", "data": None}