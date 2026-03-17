from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional


# schema/response.py
class FeedbackResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    intv_id: int                    
    intv_question_id: int
    status: str
    logic_score: int
    answer_composition_score: int
    reliability: int                # ← reliability_score → reliability 로 변경
    characteristic: str
    answer_summary: str
    strength: str
    improvement: str
    feedback_badges: list[str]
    gaze_score: int
    time_score: int
    answer_duration_ms: int
    keyword_count: int
    error_message: str | None = None

