from pydantic import BaseModel

class QuestionGenerateRequest(BaseModel):
    resume_url: str
    portfolio_url: str | None = None
    self_introduction_url: str | None = None
    job_role: str
