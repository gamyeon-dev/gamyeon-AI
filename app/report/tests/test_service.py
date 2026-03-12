import pytest
from app.report.application.service import ReportService
from app.report.infrastructure.static_score_adapter import StaticScoreAdapter
from app.report.schema.request import FeedbackItem, FeedbackStatus, InterviewMeta, ReportRequest

service = ReportService(adapter=StaticScoreAdapter())


def make_request(feedbacks: list[FeedbackItem]) -> ReportRequest:
    return ReportRequest(
        interview_id= 5,
        meta=InterviewMeta(job_category="백엔드", answered_count=len(feedbacks)),
        feedbacks=feedbacks,
    )


def make_feedback(intv_question_id: int, status=FeedbackStatus.COMPLETED, **kwargs) -> FeedbackItem:
    defaults = {
        "intv_question_id": intv_question_id,
        "question": "질문",
        "status": status,
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


# ── 성공 개수 검증 ─────────────────────────────────────────

class TestSuccessCountValidation:

    def test_raises_when_success_count_is_2(self):
        feedbacks = [make_feedback(f"q_0{i}") for i in range(1, 3)]
        with pytest.raises(ValueError, match="리포트 생성 불가"):
            service.execute(make_request(feedbacks))

    def test_raises_when_all_failed(self):
        feedbacks = [make_feedback(f"q_0{i}", status=FeedbackStatus.FAILED) for i in range(1, 5)]
        with pytest.raises(ValueError):
            service.execute(make_request(feedbacks))

    def test_passes_when_success_count_is_3(self):
        feedbacks = [make_feedback(f"q_0{i}") for i in range(1, 4)]
        result = service.execute(make_request(feedbacks))
        assert result.answered_count == 3


# ── FAILED 항목 제외 검증 ──────────────────────────────────

class TestFailedExclusion:

    def test_failed_items_excluded_from_score(self):
        feedbacks = [
            make_feedback("q_01", logic_score=100, answer_composition_score=100),
            make_feedback("q_02", logic_score=100, answer_composition_score=100),
            make_feedback("q_03", logic_score=100, answer_composition_score=100),
            make_feedback("q_04", status=FeedbackStatus.FAILED,
                          logic_score=0, answer_composition_score=0),
        ]
        result = service.execute(make_request(feedbacks))
        assert result.competency_scores.logic == 100
        assert result.answered_count == 3

    def test_failed_items_excluded_from_question_summaries(self):
        feedbacks = [
            make_feedback("q_01"),
            make_feedback("q_02"),
            make_feedback("q_03"),
            make_feedback("q_04", status=FeedbackStatus.FAILED),
        ]
        result = service.execute(make_request(feedbacks))
        ids = [q.intv_question_id for q in result.question_summaries]
        assert "q_04" not in ids


# ── ReportResult 조립 검증 ─────────────────────────────────

class TestReportResultAssembly:

    def _make_standard_request(self):
        feedbacks = [make_feedback(f"q_0{i}") for i in range(1, 7)]
        return make_request(feedbacks)

    def test_report_accuracy_is_high(self):
        result = service.execute(self._make_standard_request())
        assert result.report_accuracy == "높음"

    def test_total_score_is_average_of_5(self):
        result = service.execute(self._make_standard_request())
        cs = result.competency_scores
        expected = round((cs.logic + cs.answer_composition + cs.gaze
                          + cs.time_management + cs.keyword) / 5)
        assert result.total_score == expected

    def test_strengths_count(self):
        result = service.execute(self._make_standard_request())
        assert len(result.strengths) <= 3

    def test_weaknesses_count(self):
        result = service.execute(self._make_standard_request())
        assert len(result.weaknesses) <= 3

    def test_question_summaries_match_completed_count(self):
        result = service.execute(self._make_standard_request())
        assert len(result.question_summaries) == 6
