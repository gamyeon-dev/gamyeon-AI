from pydantic import BaseModel, Field
from typing import Optional


class KeywordCandidate(BaseModel):
    term:     str
    count:    int
    category: str


class FeedbackRequest(BaseModel):
    intv_question_id:     str
    job_role:             str
    question_text:        str
    corrected_transcript: str

    degraded:             bool = False
    reliability_score:    int  = Field(default=100, ge=0, le=100)

    gaze_score:           int  = Field(default=0,   ge=0, le=100)
    time_score:           int  = Field(default=0,   ge=0, le=100)
    answer_duration_ms:   int  = Field(default=0,   ge=0)

    keyword_candidates:   list[KeywordCandidate] = Field(default_factory=list)
