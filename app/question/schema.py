from pydantic import BaseModel

class QuestionGenerateRequest(BaseModel):
    job_role: str
    resume: str

class QuestionGenerateResponse(BaseModel):
    question: str
