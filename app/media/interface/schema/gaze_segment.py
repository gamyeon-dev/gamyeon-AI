from __future__ import annotations

from pydantic import BaseModel, Field

class GazeSegmentRequest(BaseModel):
    """
    Gaze SDK → Spring Boot → Agent Server 세그먼트 수신

    segmentSequence 기준 GazeBufferPort 정렬 삽입
    """

    class Meta(BaseModel):
        interview_id:     int = Field(..., alias="interviewId")
        question_id:      int = Field(..., alias="questionId")
        timestamp:        int = Field(..., description="세그먼트 시작 epoch ms")
        segment_sequence: int = Field(..., alias="segmentSequence", ge=0)

    class MetricsSummary(BaseModel):
        average_concentration: float = Field(..., alias="averageConcentration")
        blink_count:           int   = Field(..., alias="blinkCount")
        is_away_detected:      bool  = Field(..., alias="isAwayDetected")

    class Coordinate(BaseModel):
        x: float
        y: float

    class GazeVector(BaseModel):
        left:  "GazeSegmentRequest.Coordinate"
        right: "GazeSegmentRequest.Coordinate"

    class HeadPose(BaseModel):
        pitch: float
        yaw:   float
        roll:  float

    class RawFrame(BaseModel):
        offset_ms:  int   = Field(..., alias="offsetMs")
        confidence: float
        gaze:       "GazeSegmentRequest.GazeVector"
        head:       "GazeSegmentRequest.HeadPose"

    class Event(BaseModel):
        type:      str = Field(..., description="AWAY_START | AWAY_END")
        offset_ms: int = Field(..., alias="offsetMs")
        direction: str

    meta:            Meta
    metrics_summary: MetricsSummary = Field(..., alias="metricsSummary")
    raw_data:        list[RawFrame]  = Field(..., alias="rawData")
    events:          list[Event]     = Field(default_factory=list)

    model_config = {"populate_by_name": True}