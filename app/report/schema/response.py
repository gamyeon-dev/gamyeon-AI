from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class CompetencyScores(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True, # 
    )
    
    logic: int
    answer_composition: int
    gaze: int
    time_management: int
    keyword: int

class QuestionFeedbackDetail(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True, #  핵심: 출력할 때 무조건 alias(camelCase)로 변환해라!
    )
    characteristic: str
    strength: str
    improvement: str
    
class QuestionSummary(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True, 
    )
    index: int
    question: str
    answer_summary: str
    keywords: list[str]
    feedback: QuestionFeedbackDetail

class ReportResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True, 
    )
    
    interview_id: int
    job_category: Optional[str] = None
    answered_count: int
    avg_answer_duration_ms: int
    created_at: datetime
    reliability_score: int

    report_accuracy: str
    competency_scores: CompetencyScores
    total_score: int
    strengths: list[str]
    weaknesses: list[str]
    question_summaries: list[QuestionSummary]
