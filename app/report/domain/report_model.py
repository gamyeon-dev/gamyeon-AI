from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class CompetencyScores:
    logic: int
    answer_composition: int
    gaze: int
    time_management: int
    keyword: int

@dataclass
class QuestionFeedbackDetail:
    characteristic: str
    strength: str
    improvement: str

@dataclass
class QuestionSummary:
    intv_question_id: int
    index: int    
    question: str
    answer_summary: str
    keywords: list[str]
    feedback: QuestionFeedbackDetail

@dataclass
class ReportResult:
    intv_id: int
    job_category: Optional[str]
    answered_count: int
    avg_answer_duration_ms: int
    created_at: datetime
    report_accuracy: str
    competency_scores: CompetencyScores
    total_score: int
    strengths: list[str]
    weaknesses: list[str]
    question_summaries: list[QuestionSummary]
