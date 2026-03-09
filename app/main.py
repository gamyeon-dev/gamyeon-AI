from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.consul_helper import ConsulHelper
from dotenv import load_dotenv
import consul, os

load_dotenv()

# Configuration about consul client
consul_host = os.getenv("CONSUL_HOST", "localhost")
c = consul.Consul(host = consul_host, port = 8500)

consul_helper = ConsulHelper(host="consul")
config = consul_helper("config/agent/settings")

SERVICE_ID = config.get("SERVICE_ID", "DEFAULT-SERVER")
EC2_PUBLIC_IP = config.get("EC2_PUBLIC_IP", "0.0.0.0")

@asynccontextmanager
async def lifespan(app: FastAPI) :
    c.agent.service.register(
        name = "agent-api",
        service_id = SERVICE_ID,
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

@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "message": "AI server is running"
    }