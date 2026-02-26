from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Interview AI Server",
    description="AI Interview Simulator - AI Features",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AI server is running"}
