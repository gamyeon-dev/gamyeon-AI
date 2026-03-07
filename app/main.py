from fastapi import FastAPI
from dotenv import load_dotenv
from app.question.router import router as question_router

load_dotenv()

app = FastAPI(
    title="Interview AI Server",
    description="AI Interview Simulator - AI Features",
    version="0.1.0"
)

app.include_router(question_router, prefix="/api/ai")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AI server is running"}
