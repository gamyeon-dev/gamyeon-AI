
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv

from app.report.router import router as report_router
from app.question.router import router as question_router
from app.feedback.router import router as feedback_router
from app.core.schema import ApiResponse

import os

load_dotenv()

app = FastAPI(
    title="Interview AI Server",
    description="AI Interview Simulator - AI Features",
    version="0.1.0",
)

# ── 라우터 등록 ──────────────────────────────────────────────────
app.include_router(question_router, prefix="/api/ai")
app.include_router(feedback_router)
app.include_router(report_router)

# ── 헬스체크 ─────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AI server is running"}

# ── 전역 예외 핸들러 ─────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ApiResponse(
            success=False,
            code="CMMN-V001",
            message="입력값 유효성 검사에 실패했습니다.",
            data=None,
        ).model_dump(),
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ApiResponse(
            success=False,
            code="CMMN-I001",
            message="서버 내부 오류가 발생했습니다.",
            data=None,
        ).model_dump(),
    )


