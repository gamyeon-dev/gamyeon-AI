from pydantic import BaseModel

class QuestionGenerateResponse(BaseModel):
    questions: list[str]
