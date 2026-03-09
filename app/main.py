from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import consul, os

load_dotenv()

# Configuration about consul client
consul_host = os.getenv("CONSUL_HOST", "localhost")
c = consul.Consul(host = consul_host, port = 8500)
SERVICE_ID = "AGENT-SERVER"
EXTERNAL_HOST_IP = "172.17.0.1"
EC2_PUBLIC_IP = "15.164.229.233"

@asynccontextmanager
async def lifespan(app: FastAPI) :
    c.agent.service.register(
        name = "agentapi-app",
        service_id = SERVICE_ID,
        address = EXTERNAL_HOST_IP,
        port = 8500,
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
    return {"status": "ok", "message": "AI server is running"}