from fastapi import APIRouter, Depends

from app.feedback.application.service import FeedbackService
from app.feedback.infrastructure.di import get_feedback_service
from app.feedback.schema.request import FeedbackRequest
from app.feedback.schema.response import FeedbackResponse

router = APIRouter(prefix="/api/ai/feedback", tags=["feedback"])


@router.post("/generate", response_model=FeedbackResponse)
async def generate_feedback(
    request: FeedbackRequest,
    service: FeedbackService = Depends(get_feedback_service),
) -> FeedbackResponse:
    return await service.generate_feedback(request)
