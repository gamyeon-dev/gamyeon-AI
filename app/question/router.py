from fastapi import APIRouter
from .schema import QuestionGenerateRequest, QuestionGenerateResponse
from .service import QuestionService

router = APIRouter(prefix="/question", tags=["question"])
service = QuestionService()

@router.post("/generate", response_model=QuestionGenerateResponse)
async def generate_question(request: QuestionGenerateRequest):
    question = await service.generate(request.job_role, request.resume)
    return QuestionGenerateResponse(question=question)
