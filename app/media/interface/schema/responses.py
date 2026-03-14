from __future__ import annotations

from pydantic import BaseModel

class AcceptedData(BaseModel):
    """
    202 Accepted data 페이로드
    POST /internal/v1/gaze-batches 수락 확인
    결과는 Spring Boot Webhook으로 수신
    """
    interview_id: int
    question_id:  int


class ErrorData(BaseModel):
    """
    에러 data 페이로드.
    4xx / 5xx 에러 상세 정보.
    """
    interview_id: int | None = None
    question_id:  int | None = None
    error_code:   str
    message:      str