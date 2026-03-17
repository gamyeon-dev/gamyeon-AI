from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class FeedbackStatus(Enum):
    SUCCEED = "SUCCEED"
    SKIPPED   = "SKIPPED" #생략됐을때
    FAILED    = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"


@dataclass
class QuestionFeedback:
    intv_question_id:          int
    status:                    FeedbackStatus

    # LLM 산출
    logic_score:               Optional[int]       = None
    answer_composition_score:  Optional[int]       = None
    characteristic:            Optional[str]       = None
    answer_summary:            Optional[str]       = None
    strength:                  Optional[str]       = None
    improvement:               Optional[str]       = None
    feedback_badges:           list[str]           = field(default_factory=list)

    # media 수치
    gaze_score:                int                 = 0
    time_score:                int                 = 0
    answer_duration_ms:        int                 = 0
    keyword_count:             int                 = 0
    reliability_score:        int                 = 0


    @staticmethod
    def skipped(intv_question_id: int) -> "QuestionFeedback":
        return QuestionFeedback(
            intv_question_id         = intv_question_id,
            status                   = FeedbackStatus.FAILED,
            logic_score              = 0,
            answer_composition_score = 0,
            characteristic           = "답변 내용이 없어 평가할 수 없습니다.",
            answer_summary           = "답변이 제공되지 않았습니다.",
            strength                 = "답변이 제공되지 않았습니다.",
            improvement              = "질문에 대한 답변을 작성해 주세요.",
            feedback_badges          = ["답변 없음"],
        )

    @staticmethod
    def failed(
        intv_question_id: int,
        gaze_score:        int = 0,
        time_score:        int = 0,
        answer_duration_ms:int = 0,
        keyword_count:     int = 0,
        reliability_score: int = 0,
    ) -> "QuestionFeedback":
        return QuestionFeedback(
            intv_question_id   = intv_question_id,
            status             = FeedbackStatus.FAILED,
            characteristic     = "일시적 오류로 평가를 생성하지 못했습니다.",
            feedback_badges    = ["평가 실패"],
            gaze_score         = gaze_score,
            time_score         = time_score,
            reliability_score  = reliability_score,
            answer_duration_ms = answer_duration_ms,
            keyword_count      = keyword_count,
        )
