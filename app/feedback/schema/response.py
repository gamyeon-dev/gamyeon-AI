from pydantic import BaseModel


# schema/response.py,스프링 웹훅에 보낼 피드백 결과 모델
class FeedbackResponse(BaseModel):

    intv_id: int
    intv_question_id: int
    status: str
    logic_score: int
    answer_composition_score: int
    reliability: int  # ← reliability_score → reliability 로 변경
    characteristic: str
    answer_summary: str
    strength: str
    improvement: str
    feedback_badges: list[str]
    gaze_score: int
    time_score: int
    answer_duration_ms: int
    keyword_count: int
    error_message: str | None = None
