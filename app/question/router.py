# app/question/router.py
from fastapi import APIRouter, BackgroundTasks, Depends
from app.question.schema.response import ApiResponse  # ← 실제 위치에 맞게 import 수정
from app.question.schema.request import QuestionGenerateRequest
from app.question.infrastructure.di import get_question_service

router = APIRouter(prefix="/internal/v1/questions", tags=["question"])


@router.post("/generate", status_code=202, response_model=ApiResponse[None])
async def generate_questions(
    request:          QuestionGenerateRequest,
    background_tasks: BackgroundTasks,
    service=          Depends(get_question_service),
) -> ApiResponse[None]:
    background_tasks.add_task(service.run, request)
    return ApiResponse[None](
        success=True,
        code="S000",
        message="success",
        data=None,
    )
