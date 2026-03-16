from enum import Enum
from pydantic import BaseModel, model_validator
from typing import Optional


class FeedbackStatus(str, Enum):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True, # Spring이 보낸 camelCase를 받아들임
    )   
    
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class FeedbackItem(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True, # Spring이 보낸 camelCase를 받아들임
    )
        
    intv_question_id: int
    index: int 
    question: str
    status: FeedbackStatus
    logic_score: int
    answer_composition_score: int
    answer_summary: str
    characteristic: str
    strength: str
    improvement: str
    feedback_badges: list[str]
    gaze_score: int
    time_score: int
    keyword_count: int
    answer_duration_ms: int


class InterviewMeta(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True, # Spring이 보낸 camelCase를 받아들임
    )
    job_category: Optional[str] = None
    answered_count: int


class ReportRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True, # Spring이 보낸 camelCase를 받아들임
    )
    interview_id: int
    meta: InterviewMeta
    feedbacks: list[FeedbackItem]

    @model_validator(mode="after")
    def sync_answered_count(self) -> "ReportRequest":
        self.meta.answered_count = len(self.feedbacks)
        return self
