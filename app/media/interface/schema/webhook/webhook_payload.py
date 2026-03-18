"""
Agent Server → Spring Boot Webhook 전송 페이로드 스키마

전송 채널:
- to_spring_webhook_payload(): STT + Keywords (처리 완료)
- to_failed_payload():         에러 정보 (처리 실패)
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# 하위 Payload
class WordTimestampPayload(BaseModel):
    word: str
    start: float
    end: float
    probability: float


class CorrectionPayload(BaseModel):
    original: str
    corrected: str
    position: int
    confidence: float
    type: str  # "phonetic" | "term"


class TranscriptPayload(BaseModel):
    rawTranscript: str
    phoneticTranscript: str
    correctedTranscript: str
    corrections: list[CorrectionPayload]
    wordTimestamps: list[WordTimestampPayload]


class KeywordCandidatePayload(BaseModel):
    term: str
    count: int
    category: str


class KeywordsPayload(BaseModel):
    candidates: list[KeywordCandidatePayload]


# 최상위 Webhook 페이로드 (DONE)
class WebhookSuccessPayload(BaseModel):
    """
    STT + Keywords 처리 완료 Webhook 페이로드
    Spring Boot가 수신 후 DB 저장 + 프론트 전송 담당
    """

    interview_id:  int                  = Field(..., alias="intvId")
    question_id:   int                  = Field(..., alias="questionSetId")
    degraded:      bool
    answer_text:   TranscriptPayload    = Field(..., alias="answerText")
    keywords:      KeywordsPayload
    error_message: None                 = Field(None, alias="errorMessage")


# 처리 실패 페이로드 (FAILED)
class WebhookFailedPayload(BaseModel):
    """
    파이프라인 FAILED 페이로드
    STT 실패 등 복구 불가 오류 시 전송
    """

    interview_id:  int              = Field(..., alias="intvId")
    question_id:   int              = Field(..., alias="questionSetId")
    status:        Literal["FAILED"] = "FAILED"
    answer_text:   None             = Field(None, alias="answerText")
    error_message: str              = Field(..., alias="errorMessage")
