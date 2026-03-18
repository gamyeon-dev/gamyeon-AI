from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing import List
from enum import Enum

class FeedbackStatus(str, Enum):
    SUCCEED = "SUCCEED"
    FAILED = "FAILED"

class FeedbackItem(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    
    question_set_id: int 
    index: int
    question_content: str 
    status: FeedbackStatus
    reliability: int
    logic_score: int
    answer_composition_score: int 
    gaze_score: int 
    time_score: int 
    answer_duration_ms: int 
    keyword_count: int 
    characteristic: str
    answer_summary: str
    strength: str
    improvement: str
    feedback_badges: List[str] 

class ReportGenerateRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    intv_id: int
    user_id: int 
    callback: str
    feedbacks: List[FeedbackItem]
