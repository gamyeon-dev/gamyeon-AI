# app/report/infrastructure/static_score_adapter.py
from typing import List
from app.report.application.port.report_generator_port import ReportGeneratorPort
from app.report.schema.request import FeedbackItem
from app.report.domain.report_model import (
    ReportResult, CompetencyScores, QuestionFeedbackDetail, QuestionSummary
)
from datetime import datetime, timezone

class StaticScoreAdapter(ReportGeneratorPort):
    """
    ReportGeneratorPort 구현체 — 완전 정적 처리
    LLM 호출 없음, 순수 계산 로직만 포함
    """

    def generate(self, feedbacks: list[FeedbackItem], intv_id: int) -> ReportResult:
        """
        전체 리포트 생성 — Port 단일 메서드
        """
        # 1. 역량 점수 산정
        logic           = self.calc_logic(feedbacks)
        answer_comp     = self.calc_answer_composition(feedbacks)
        gaze            = self.calc_gaze(feedbacks)
        time_management = self.calc_time_management(feedbacks)
        keyword         = self.calc_keyword(feedbacks)

        # 2. 총점 산정
        total_score = self.calc_total_score(
            logic, answer_comp, gaze, time_management, keyword
        )

        # 3. 리포트 정확도 산정
        avg_score = sum(
            f.logic_score + f.answer_composition_score for f in feedbacks
        ) / (len(feedbacks) * 2)
        report_accuracy = self.calc_accuracy(len(feedbacks), avg_score)

        # 4. 강점 / 약점 추출
        strengths  = self.extract_strengths(feedbacks)
        weaknesses = self.extract_weaknesses(feedbacks)

        # 5. 문항별 요약 빌드
        raw_summaries = self.build_question_summaries(feedbacks)
        question_summaries = [
            QuestionSummary(
                intv_question_id=s["intv_question_id"],
                index=s["index"],
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

        # 6. ReportResult 조립
        return ReportResult(
            intv_id=intv_id,
            job_category=None,  # Spring에서 처리
            answered_count=len(feedbacks),
            avg_answer_duration_ms=self.calc_avg_duration_ms(feedbacks),
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

    # ── 역량 점수 ──────────────────────────────────────────

    def calc_logic(self, feedbacks: list[FeedbackItem]) -> int:
        return round(sum(f.logic_score for f in feedbacks) / len(feedbacks))

    def calc_answer_composition(self, feedbacks: list[FeedbackItem]) -> int:
        return round(sum(f.answer_composition_score for f in feedbacks) / len(feedbacks))

    def calc_gaze(self, feedbacks: list[FeedbackItem]) -> int:
        return round(sum(f.gaze_score for f in feedbacks) / len(feedbacks))

    def calc_time_management(self, feedbacks: list[FeedbackItem]) -> int:
        """time_score 문항별 평균"""
        return round(sum(f.time_score for f in feedbacks) / len(feedbacks))

    def calc_keyword(self, feedbacks: list[FeedbackItem]) -> int:
        avg_count = sum(f.keyword_count for f in feedbacks) / len(feedbacks)
        if avg_count == 0:
            return 10
        elif avg_count < 2:
            return 40
        elif avg_count <= 3:
            return 80
        else:
            return 60

    def calc_total_score(self, logic: int, answer_composition: int, gaze: int,
                         time_management: int, keyword: int) -> int:
        return round((logic + answer_composition + gaze + time_management + keyword) / 5)

    # ── 리포트 정확도 ──────────────────────────────────────

    def calc_accuracy(self, success_count: int, avg_score: float) -> str:
        if success_count >= 6:
            level = "높음"
        elif success_count == 5:
            level = "중간"
        else:
            level = "낮음"

        if avg_score <= 40:
            level = self._downgrade(level)

        return level

    def _downgrade(self, level: str) -> str:
        return {"높음": "중간", "중간": "낮음", "낮음": "낮음"}[level]

    # ── 강점 / 약점 추출 ───────────────────────────────────

    def extract_strengths(self, feedbacks: list[FeedbackItem]) -> list[str]:
        sorted_feedbacks = sorted(
            feedbacks,
            key=lambda f: f.logic_score + f.answer_composition_score,
            reverse=True
        )
        return [f.strength for f in sorted_feedbacks[:3]]

    def extract_weaknesses(self, feedbacks: list[FeedbackItem]) -> list[str]:
        sorted_feedbacks = sorted(
            feedbacks,
            key=lambda f: f.logic_score + f.answer_composition_score
        )
        return [f.improvement for f in sorted_feedbacks[:3]]

    # ── 문항별 요약 빌드 ───────────────────────────────────

    def build_question_summaries(self, feedbacks: list[FeedbackItem]) -> list[dict]:
        return [
            {
                "intv_question_id": f.question_set_id,
                "index": f.index,
                "question": f.question_content,
                "answer_summary": f.answer_summary,
                "keywords": f.feedback_badges,
                "feedback": {
                    "characteristic": f.characteristic,
                    "strength": f.strength,
                    "improvement": f.improvement,
                },
            }
            for f in feedbacks
        ]

    # ── 평균 답변 시간 ─────────────────────────────────────

    def calc_avg_duration_ms(self, feedbacks: list[FeedbackItem]) -> int:
        return round(sum(f.answer_duration_ms for f in feedbacks) / len(feedbacks))
