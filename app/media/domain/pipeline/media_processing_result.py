from __future__ import annotations
from dataclasses import dataclass

from media.schema.webhook import (
    WebhookSuccessPayload,
    WebhookFailedPayload,
    TranscriptPayload,
    CorrectionPayload,
    WordTimestampPayload,
    KeywordsPayload,
    KeywordCandidatePayload,
)

@dataclass(frozen=True)
class MediaProcessingResult:
    def to_spring_webhook_payload(self) -> WebhookSuccessPayload:
        return WebhookSuccessPayload(
            interviewId=self.interview_id,
            questionId= self.question_id,
            degraded=   self.degraded,
            transcript= TranscriptPayload(
                rawTranscript=      self.transcript.raw_transcript,
                correctedTranscript=self.transcript.corrected_transcript,
                corrections=[
                    CorrectionPayload(
                        original=  c.original,
                        corrected= c.corrected,
                        position=  c.position,
                        confidence=c.confidence,
                        type=      c.type.value,
                    )
                    for c in self.transcript.corrections
                ],
                wordTimestamps=[
                    WordTimestampPayload(
                        word=       wt.word,
                        start=      wt.start,
                        end=        wt.end,
                        probability=wt.probability,
                    )
                    for wt in self.transcript.word_timestamps
                ],
            ),
            keywords=KeywordsPayload(
                candidates=[
                    KeywordCandidatePayload(
                        term=    k.term,
                        count=   k.count,
                        category=k.category,
                    )
                    for k in self.keywords.candidates
                ]
            ),
        )

    def to_failed_payload(
        self,
        error_code: str,
        message:    str,
    ) -> WebhookFailedPayload:
        return WebhookFailedPayload(
            interviewId=self.interview_id,
            questionId= self.question_id,
            errorCode=  error_code,
            message=    message,
        )