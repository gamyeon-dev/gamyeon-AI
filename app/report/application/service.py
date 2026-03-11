from datetime import datetime, timezone

from app.report.domain.report_model import (
    CompetencyScores, QuestionFeedbackDetail, QuestionSummary, ReportResult
)
from app.report.infrastructure.static_score_adapter import StaticScoreAdapter
from app.report.schema.request import FeedbackStatus, ReportRequest


class ReportService:

    def __init__(self, adapter: StaticScoreAdapter):
        self.adapter = adapter

    def execute(self, request: ReportRequest) -> ReportResult:
        # 1. COMPLETED 항목만 필터링
        completed = [f for f in request.feedbacks if f.status == FeedbackStatus.COMPLETED]
        success_count = len(completed)

        # 2. 성공 개수 검증 (2개 이하 → 호출부에서 422 처리)
        if success_count <= 2:
            raise ValueError(f"리포트 생성 불가: 성공한 피드백이 {success_count}개입니다.")

        # 3. 역량 점수 산정
        logic           = self.adapter.calc_logic(completed)
        answer_comp     = self.adapter.calc_answer_composition(completed)
        gaze            = self.adapter.calc_gaze(completed)
        time_management = self.adapter.calc_time_management(completed)
        keyword         = self.adapter.calc_keyword(completed)

        # 4. 총점 산정
        total_score = self.adapter.calc_total_score(
            logic, answer_comp, gaze, time_management, keyword
        )

        # 5. 리포트 정확도 산정
        avg_score = sum(f.logic_score + f.answer_composition_score for f in completed) / (success_count * 2)
        report_accuracy = self.adapter.calc_accuracy(success_count, avg_score)

        # 6. 강점 / 약점 추출
        strengths  = self.adapter.extract_strengths(completed)
        weaknesses = self.adapter.extract_weaknesses(completed)

        # 7. 문항별 요약 빌드
        raw_summaries = self.adapter.build_question_summaries(completed)
        question_summaries = [
            QuestionSummary(
                intv_question_id=s["intv_question_id"],
                question=s["question"],
                answer_summary=s["answer_summary"],
                keywords=s["keywords"],
                feedback=QuestionFeedbackDetail(
                    characteristic=s["feedback"]["characteristic"],
                    strength=s["feedback"]["strength"],
                    improvement=s["feedback"]["improvement"],
                ),
            )
            for s in raw_summaries
        ]

        # 8. ReportResult 조립
        return ReportResult(
            interview_id=request.interview_id,
            job_category=request.meta.job_category,
            answered_count=success_count,
            avg_answer_duration_ms=self.adapter.calc_avg_duration_ms(completed),
            created_at=datetime.now(timezone.utc),
            report_accuracy=report_accuracy,
            competency_scores=CompetencyScores(
                logic=logic,
                answer_composition=answer_comp,
                gaze=gaze,
                time_management=time_management,
                keyword=keyword,
            ),
            total_score=total_score,
            strengths=strengths,
            weaknesses=weaknesses,
            question_summaries=question_summaries,
        )
