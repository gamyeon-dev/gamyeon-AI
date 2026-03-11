from app.report.schema.request import FeedbackItem


class StaticScoreAdapter:

    # ── 역량 점수 ──────────────────────────────────────────

    def calc_logic(self, feedbacks: list[FeedbackItem]) -> int:
        return round(sum(f.logic_score for f in feedbacks) / len(feedbacks))

    def calc_answer_composition(self, feedbacks: list[FeedbackItem]) -> int:
        return round(sum(f.answer_composition_score for f in feedbacks) / len(feedbacks))

    def calc_gaze(self, feedbacks: list[FeedbackItem]) -> int:
        return round(sum(f.gaze_score for f in feedbacks) / len(feedbacks))

    def calc_time_management(self, feedbacks: list[FeedbackItem]) -> int:
        avg_seconds = sum(f.answer_duration_ms for f in feedbacks) / len(feedbacks) / 1000
        if avg_seconds < 30:
            return 40
        elif avg_seconds <= 50:
            return 85
        elif avg_seconds <= 55:
            return 100
        else:
            return 60

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
                "intv_question_id": f.intv_question_id,
                "question": f.question,
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
