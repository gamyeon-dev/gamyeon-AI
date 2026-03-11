from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core import ConsulHelper
from dotenv import load_dotenv
from app.question.router import router as question_router
import consul, os, uuid

load_dotenv()

# Configuration about consul client
consul_host = os.getenv("CONSUL_HOST", "localhost")
c = consul.Consul(host = consul_host, port = 8500)

@asynccontextmanager
async def lifespan(app: FastAPI) :
    consul_helper = ConsulHelper(host="consul")
    config = consul_helper.get_config("config/agent/settings")

    SERVICE_ID = config.get("SERVICE_ID", "DEFAULT-SERVER")
    EXTERNAL_HOST_IP = config.get("EXTERNAL_HOST_IP", "127.0.0.1")
    EC2_PUBLIC_IP = config.get("EC2_PUBLIC_IP", "0.0.0.0")

    # UUID를 사용하여 매번 다른 ID 생성
    unique_id = f"{SERVICE_ID}:{uuid.uuid4()}" 

    c.agent.service.register(
        name = SERVICE_ID,
        service_id = unique_id,
        address = EXTERNAL_HOST_IP,
        port = 8000,
        check = consul.Check.http(f"http://{EC2_PUBLIC_IP}:8000/health", interval = "10s")
    )
    print("Consul 등록 완료")

    yield # 서버 실행

    c.agent.service.deregister(SERVICE_ID)
    print("Consul 등록 해제")

app = FastAPI(
    title="Interview AI Server",
    description="AI Interview Simulator - AI Features",
    version="0.1.0",
    lifespan = lifespan
)

app.include_router(question_router, prefix="/api/ai")

@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "message": "AI server is running"
    }