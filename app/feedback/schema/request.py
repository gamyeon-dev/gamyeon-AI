from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional


class KeywordCandidate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True, # Spring이 보낸 camelCase를 받아들임
    )
    
    term:     str
    count:    int
    category: str


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator= to_camel,
        populate_by_name=True, # Spring이 보낸 camelCase를 받아들임
    )
    
    intv_question_id:     int
    question_text:        str
    corrected_transcript: str

    degraded:             bool = False
    reliability_score:    int  = Field(default=100, ge=0, le=100)

    gaze_score:           int  = Field(default=0,   ge=0, le=100)
    time_score:           int  = Field(default=0,   ge=0, le=100)
    answer_duration_ms:   int  = Field(default=0,   ge=0)

    keyword_candidates:   list[KeywordCandidate] = Field(default_factory=list)
