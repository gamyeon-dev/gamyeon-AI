from fastapi import APIRouter
from app.question.schema.request import QuestionGenerateRequest
from app.question.schema.response import QuestionGenerateResponse
from app.question.infrastructure.di import (
    get_s3_download_port,
    get_pdf_extract_port,
    get_structuring_port,
    get_question_gen_port,
)
from app.question.application.service import QuestionService

router = APIRouter(prefix="/question", tags=["question"])

@router.post("/generate", response_model=QuestionGenerateResponse)
async def generate_question(request: QuestionGenerateRequest):
    service = QuestionService(
        s3_download_port=get_s3_download_port(),
        pdf_extract_port=get_pdf_extract_port(),
        structuring_port=get_structuring_port(),
        question_gen_port=get_question_gen_port(),
    )
    questions = await service.parse_and_generate(
        resume_url=request.resume_url,
        job_role=request.job_role,
        portfolio_url=request.portfolio_url,
        self_introduction_url=request.self_introduction_url,
    )
    return QuestionGenerateResponse(questions=questions)
