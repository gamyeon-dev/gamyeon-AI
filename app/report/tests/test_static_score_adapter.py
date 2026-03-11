import pytest
from app.report.infrastructure.static_score_adapter import StaticScoreAdapter
from app.report.schema.request import FeedbackItem, FeedbackStatus

adapter = StaticScoreAdapter()


def make_feedback(**kwargs) -> FeedbackItem:
    defaults = {
        "intv_question_id": "q_01",
        "question": "본인의 강점을 말해주세요",
        "status": FeedbackStatus.COMPLETED,
        "logic_score": 80,
        "answer_composition_score": 75,
        "answer_summary": "summary",
        "characteristic": "characteristic",
        "strength": "strength",
        "improvement": "improvement",
        "feedback_badges": ["badge1"],
        "gaze_score": 80,
        "time_score": 90,
        "keyword_count": 2,
        "answer_duration_ms": 52000,
    }
    defaults.update(kwargs)
    return FeedbackItem(**defaults)


# ── calc_time_management ───────────────────────────────────

class TestCalcTimeManagement:

    def test_under_30s(self):
        f = [make_feedback(answer_duration_ms=29000)]
        assert adapter.calc_time_management(f) == 40

    def test_boundary_30s(self):
        f = [make_feedback(answer_duration_ms=30000)]
        assert adapter.calc_time_management(f) == 85

    def test_between_30s_50s(self):
        f = [make_feedback(answer_duration_ms=40000)]
        assert adapter.calc_time_management(f) == 85

    def test_boundary_50s(self):
        f = [make_feedback(answer_duration_ms=50000)]
        assert adapter.calc_time_management(f) == 85

    def test_between_50s_55s(self):
        f = [make_feedback(answer_duration_ms=52000)]
        assert adapter.calc_time_management(f) == 100

    def test_boundary_55s(self):
        f = [make_feedback(answer_duration_ms=55000)]
        assert adapter.calc_time_management(f) == 100

    def test_over_55s(self):
        f = [make_feedback(answer_duration_ms=56000)]
        assert adapter.calc_time_management(f) == 60


# ── calc_keyword ───────────────────────────────────────────

class TestCalcKeyword:

    def test_zero(self):
        feedbacks = [make_feedback(keyword_count=0)] * 3
        assert adapter.calc_keyword(feedbacks) == 10

    def test_one(self):
        feedbacks = [make_feedback(keyword_count=1)] * 3
        assert adapter.calc_keyword(feedbacks) == 40

    def test_two(self):
        feedbacks = [make_feedback(keyword_count=2)] * 3
        assert adapter.calc_keyword(feedbacks) == 80

    def test_three(self):
        feedbacks = [make_feedback(keyword_count=3)] * 3
        assert adapter.calc_keyword(feedbacks) == 80

    def test_over_three(self):
        feedbacks = [make_feedback(keyword_count=4)] * 3
        assert adapter.calc_keyword(feedbacks) == 60


# ── calc_accuracy ──────────────────────────────────────────

class TestCalcAccuracy:

    def test_high(self):
        assert adapter.calc_accuracy(6, 70.0) == "높음"

    def test_medium(self):
        assert adapter.calc_accuracy(5, 70.0) == "중간"

    def test_low(self):
        assert adapter.calc_accuracy(4, 70.0) == "낮음"

    def test_downgrade_high_to_medium(self):
        assert adapter.calc_accuracy(6, 40.0) == "중간"

    def test_downgrade_medium_to_low(self):
        assert adapter.calc_accuracy(5, 40.0) == "낮음"

    def test_downgrade_low_stays_low(self):
        assert adapter.calc_accuracy(4, 40.0) == "낮음"

    def test_boundary_avg_score_41_no_downgrade(self):
        assert adapter.calc_accuracy(6, 41.0) == "높음"


# ── extract_strengths / weaknesses ────────────────────────

class TestExtractStrengthsWeaknesses:

    def _make_feedbacks(self):
        return [
            make_feedback(intv_question_id=f"q_0{i}",
                          logic_score=s, answer_composition_score=s,
                          strength=f"strength_{i}", improvement=f"improvement_{i}")
            for i, s in enumerate([90, 70, 50, 30, 10], start=1)
        ]

    def test_strengths_top3(self):
        result = adapter.extract_strengths(self._make_feedbacks())
        assert result == ["strength_1", "strength_2", "strength_3"]

    def test_weaknesses_bottom3(self):
        result = adapter.extract_weaknesses(self._make_feedbacks())
        assert result == ["improvement_5", "improvement_4", "improvement_3"]
