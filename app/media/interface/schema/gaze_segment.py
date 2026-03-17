from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

class GazeSegmentRequest(BaseModel):
    """
    Gaze SDK → Spring Boot → Agent Server 세그먼트 수신

    segmentSequence 기준 GazeBufferPort 정렬 삽입
    """

    model_config = ConfigDict(
        alias_generator=to_camel,      # ← 추가: snake_case → camelCase 자동 변환
        populate_by_name=True,
    )
    
    class Meta(BaseModel):
        interview_id:     int = Field(..., alias="intvId")
        question_id:      int = Field(..., alias="questionSetId")
        timestamp:        int = Field(..., description="세그먼트 시작 epoch ms")
        segment_sequence: int = Field(..., alias="segmentSequence", ge=0)

    class MetricsSummary(BaseModel):
        average_concentration: float
        blink_count:           int
        is_away_detected:      bool

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
        offset_ms:  int
        confidence: float
        gaze:       "GazeSegmentRequest.GazeVector"
        head:       "GazeSegmentRequest.HeadPose"

    class Event(BaseModel):
        type:      str = Field(..., description="AWAY_START | AWAY_END")
        offset_ms: int
        direction: str

    meta:            Meta
    metrics_summary: MetricsSummary
    raw_data:        list[RawFrame]
    events:          list[Event]     = Field(default_factory=list)

    model_config = {"populate_by_name": True}
