import os
import uuid
from contextlib import asynccontextmanager

import consul
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core import ConsulHelper
from app.core.schema import ApiResponse
from app.feedback.router import router as feedback_router
from app.media.interface.router import router as media_router
from app.question.router import router as question_router
from app.report.router import router as report_router

load_dotenv()

# Configuration about consul client
consul_host = os.getenv("CONSUL_HOST", "localhost")
c = consul.Consul(host=consul_host, port=8500)


@asynccontextmanager
async def lifespan(app: FastAPI):
    consul_helper = ConsulHelper(host="consul")
    config = consul_helper.get_config("config/agent/settings")

    SERVICE_ID = config.get("SERVICE_ID", "DEFAULT-SERVER")
    EXTERNAL_HOST_IP = config.get("EXTERNAL_HOST_IP", "127.0.0.1")
    EC2_PUBLIC_IP = config.get("EC2_PUBLIC_IP", "0.0.0.0")

    # UUID를 사용하여 매번 다른 ID 생성
    unique_id = f"{SERVICE_ID}:{uuid.uuid4()}"

    c.agent.service.register(
        name=SERVICE_ID,
        service_id=unique_id,
        address=EXTERNAL_HOST_IP,
        port=8000,
        check=consul.Check.http(f"http://{EC2_PUBLIC_IP}:8000/health", interval="10s"),
    )
    print("Consul 등록 완료")

    yield  # 서버 실행

    c.agent.service.deregister(SERVICE_ID)
    print("Consul 등록 해제")


app = FastAPI(
    title="Interview AI Server",
    description="AI Interview Simulator - AI Features",
    version="0.1.0",
    lifespan=lifespan,
)


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


# ── 라우터 등록 ──────────────────────────────────────────────────
app.include_router(feedback_router)
app.include_router(question_router)
app.include_router(report_router)
app.include_router(media_router)
