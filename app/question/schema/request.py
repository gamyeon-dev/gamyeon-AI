from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class QuestionGenerateRequest(BaseModel):
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True, # Spring이 보낸 camelCase를 받아들임
    )
    
    resume_url: str
    portfolio_url: str | None = None
    self_introduction_url: str | None = None
    job_role: str
