# app/media/domain/pipeline/aggregate.py
from __future__ import annotations
from dataclasses import dataclass

from .. transcript.transcript_state import TranscriptState
from ..gaze.gaze_result import GazeResult
from ..keyword.keyword_result import KeywordResult
from ..scoring.time_score import TimeScore
from ..scoring.reliability_score import ReliabilityScore

@dataclass(frozen=True)
class MediaProcessingResult :
    """
    파이프라인 완료 집계 상태 — 최상위 Aggregate Root

    degraded:
    - S5 LLM 교정 실패 OR Gaze 버퍼 비어있음 → True
    - status=DONE, 일부 데이터 누락 표시
    """
    interview_id: str
    question_id:  str
    transcript:   TranscriptState
    keywords:     KeywordResult
    gaze:         GazeResult
    time:         TimeScore
    reliability:  ReliabilityScore
    degraded:     bool = False

    def to_spring_webhook_payload(self) -> dict :
        """
        Spring Boot Webhook 전송 페이로드
        STT 결과 + Keywords만 포함
        Spring Boot가 수신 후 DB 저장 + 프론트 전송 담당
        """
        return {
            "interviewId": self.interview_id,
            "questionId":  self.question_id,
            "status":      "DONE",
            "degraded":    self.degraded,
            "transcript": {
                "rawTranscript":       self.transcript.raw_transcript,
                "correctedTranscript": self.transcript.corrected_transcript,
                "corrections": [
                    {
                        "original":   c.original,
                        "corrected":  c.corrected,
                        "position":   c.position,
                        "confidence": c.confidence,
                        "type":       c.type.value,
                    }
                    for c in self.transcript.corrections
                ],
                "wordTimestamps": [
                    {
                        "word":        wt.word,
                        "start":       wt.start,
                        "end":         wt.end,
                        "probability": wt.probability,
                    }
                    for wt in self.transcript.word_timestamps
                ],
            },
            "keywords": {
                "candidates": [
                    {
                        "term":     k.term,
                        "count":    k.count,
                        "category": k.category,
                    }
                    for k in self.keywords.candidates
                ]
            },
        }

    def to_feedback_event_payload(self) -> dict :
        """
        feedback 도메인 내부 이벤트 페이로드
        STT + Keywords + 전체 분석 데이터 포함
        DB 조회 없이 이 페이로드만으로 feedback 처리 가능

        phoneticCorrected: MVP-2 STT 인식률 분석용 포함
        """
        base = self.to_spring_webhook_payload()
        return {
            **base,
            "gaze": {
                "gazeScore": self.gaze.gaze_score,
                "summary": {
                    "avgConcentration": self.gaze.summary.avg_concentration,
                    "awayCount":        self.gaze.summary.away_count,
                    "awayTotalMs":      self.gaze.summary.away_total_ms,
                    "segmentCoverage":  self.gaze.summary.segment_coverage,
                    "avgConfidence":    self.gaze.summary.avg_confidence,
                },
                "segments": [
                    {
                        "segmentSequence": seg.meta.segment_sequence,
                        "timestamp":       seg.meta.timestamp,
                        "metricsSummary": {
                            "averageConcentration": seg.metrics_summary.average_concentration,
                            "blinkCount":           seg.metrics_summary.blink_count,
                            "isAwayDetected":       seg.metrics_summary.is_away_detected,
                        },
                        "rawData": [
                            {
                                "offsetMs":   f.offset_ms,
                                "confidence": f.confidence,
                                "gaze": {
                                    "left":  {"x": f.gaze.left.x,  "y": f.gaze.left.y},
                                    "right": {"x": f.gaze.right.x, "y": f.gaze.right.y},
                                },
                                "head": {
                                    "pitch": f.head.pitch,
                                    "yaw":   f.head.yaw,
                                    "roll":  f.head.roll,
                                },
                            }
                            for f in seg.raw_data
                        ],
                        "events": [
                            {
                                "type":      e.type.value,
                                "offsetMs":  e.offset_ms,
                                "direction": e.direction.value,
                            }
                            for e in seg.events
                        ],
                    }
                    for seg in self.gaze.segments
                ],
            },
            "time": {
                "timeScore":        self.time.time_score,
                "answerDurationMs": self.time.answer_duration_ms,
                "limitMs":          self.time.limit_ms,
                "ratio":            self.time.ratio,
            },
            "reliability": {
                "score": self.reliability.score,
                "grade": self.reliability.grade.value,
                "factors": {
                    "questionSuccessRate": self.reliability.factors.question_success_rate,
                    "segmentCoverage":     self.reliability.factors.segment_coverage,
                    "avgWordConfidence":   self.reliability.factors.avg_word_confidence,
                },
            },
            "phoneticCorrected": self.transcript.phonetic_corrected,
        }

    def to_failed_payload(self, error_code: str, message: str) -> dict :
        """FAILED 시 Spring Boot 전송 페이로드"""
        return {
            "interviewId": self.interview_id,
            "questionId":  self.question_id,
            "status":      "FAILED",
            "degraded":    False,
            "errorCode":   error_code,
            "message":     message,
        }