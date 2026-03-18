from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

if TYPE_CHECKING:
    from app.report.domain.report_model import ReportResult


class CallbackStatus(str, Enum):
    SUCCEED = "SUCCEED"
    FAILED = "FAILED"


class QuestionFeedbackDetail(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    characteristic: str
    strength: str
    improvement: str


class QuestionSummary(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    index: int
    question_set_id: int  # → questionSetId
    question: str
    answer_summary: str  # → answerSummary
    feedback_badges: List[str]  # → feedbackBadges
    feedback: QuestionFeedbackDetail


class CompetencyScores(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    logic: int
    answer_composition: int  # → answerComposition
    gaze: int
    time_management: int  # → timeManagement
    keyword: int


class ReportResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    total_score: int
    report_accuracy: str
    job_category: Optional[str] = None
    answered_count: int
    avg_answer_duration_ms: int
    created_at: datetime
    competency_scores: CompetencyScores
    strengths: List[str]
    weaknesses: List[str]
    question_summaries: List[QuestionSummary]

    @classmethod
    def from_domain(cls, result: ReportResult) -> ReportResponse:
        return cls(
            total_score=result.total_score,
            report_accuracy=result.report_accuracy,
            job_category=result.job_category,
            answered_count=result.answered_count,
            avg_answer_duration_ms=result.avg_answer_duration_ms,
            created_at=result.created_at,
            competency_scores=CompetencyScores(
                logic=result.competency_scores.logic,
                answer_composition=result.competency_scores.answer_composition,
                gaze=result.competency_scores.gaze,
                time_management=result.competency_scores.time_management,
                keyword=result.competency_scores.keyword,
            ),
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            question_summaries=[
                QuestionSummary(
                    index=qs.index,
                    question_set_id=qs.intv_question_id,
                    question=qs.question,
                    answer_summary=qs.answer_summary,
                    feedback_badges=qs.keywords,
                    feedback=QuestionFeedbackDetail(
                        characteristic=qs.feedback.characteristic,
                        strength=qs.feedback.strength,
                        improvement=qs.feedback.improvement,
                    ),
                )
                for qs in result.question_summaries
            ],
        )


class ReportCallbackPayload(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )
    intv_id: int  # → intvId
    user_id: int  # → userId
    status: CallbackStatus
    report: Optional[ReportResponse] = None
    error_message: Optional[str] = None  # → errorMessage

    @classmethod
    def from_result(
        cls, intv_id: int, user_id: int, result: ReportResult
    ) -> ReportCallbackPayload:
        return cls(
            intv_id=intv_id,
            user_id=user_id,
            status=CallbackStatus.SUCCEED,
            report=ReportResponse.from_domain(result),
            error_message=None,
        )

    @classmethod
    def failed(
        cls, intv_id: int, user_id: int, error_message: str
    ) -> ReportCallbackPayload:
        return cls(
            intv_id=intv_id,
            user_id=user_id,
            status=CallbackStatus.FAILED,
            report=None,
            error_message=error_message,
        )
