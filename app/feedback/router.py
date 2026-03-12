from fastapi import APIRouter, Depends
from app.core.schema import ApiResponse
from app.feedback.application.service import FeedbackService
from app.feedback.infrastructure.di import get_feedback_service
from app.feedback.schema.request import FeedbackRequest
from app.feedback.schema.response import FeedbackResponse

router = APIRouter(prefix="/internal/v1/feedback", tags=["feedback"])


@router.post("/generate", response_model=ApiResponse[FeedbackResponse])
async def generate_feedback(
    request: FeedbackRequest,
    service: FeedbackService = Depends(get_feedback_service),
) -> ApiResponse[FeedbackResponse]:

    result = await service.generate_feedback(request)

    return ApiResponse(
        success = True,
        code    = "FDBK-S000",
        message = "success",
        data    = result,
    )
