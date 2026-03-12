from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CompetencyScores(BaseModel):
    logic: int
    answer_composition: int
    gaze: int
    time_management: int
    keyword: int

class QuestionFeedbackDetail(BaseModel):
    characteristic: str
    strength: str
    improvement: str

class QuestionSummary(BaseModel):
    index: int
    question: str
    answer_summary: str
    keywords: list[str]
    feedback: QuestionFeedbackDetail

class ReportResponse(BaseModel):
    interview_id: int
    job_category: Optional[str] = None
    answered_count: int
    avg_answer_duration_ms: int
    created_at: datetime
    report_accuracy: str
    competency_scores: CompetencyScores
    total_score: int
    strengths: list[str]
    weaknesses: list[str]
    question_summaries: list[QuestionSummary]
