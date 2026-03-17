# app/media/interface/mapper.py
"""
인바운드 스키마 → 도메인/커맨드 변환.

책임:
  schema(Pydantic) → domain/command(frozen dataclass) 변환만 담당.
  비즈니스 로직 없음. 유효성 검사 없음 (Pydantic이 담당).
"""

from __future__ import annotations

from media.interface.schema import ProcessMediaRequest, GazeSegmentRequest
from media.application.service import ProcessMediaCommand
from media.domain import (
    GazeSegment, GazeSegmentMeta, GazeMetricsSummary,
    GazeCoordinate, GazeVector, HeadPose,
    GazeRawFrame, GazeEvent, GazeEventType, GazeDirection,
)

class MediaMapper:

    @staticmethod
    def to_process_command(req: ProcessMediaRequest) -> ProcessMediaCommand:
        """ProcessMediaRequest → ProcessMediaCommand."""
        return ProcessMediaCommand(
            interview_id=  req.interview_id,
            question_id=   req.question_id,
            s3_key=        req.s3_key,
            tech_stack=    tuple(req.tech_stack),
            interview_type=req.interview_type,
        )

    @staticmethod
    def to_gaze_segment(req: GazeSegmentRequest) -> GazeSegment:
        """GazeSegmentRequest → GazeSegment 도메인 객체."""
        return GazeSegment(
            meta=GazeSegmentMeta(
                interview_id=    req.meta.interview_id,
                question_id=     req.meta.question_id,
                timestamp=       req.meta.timestamp,
                segment_sequence=req.meta.segment_sequence,
            ),
            metrics_summary=GazeMetricsSummary(
                average_concentration=req.metrics_summary.average_concentration,
                blink_count=          req.metrics_summary.blink_count,
                is_away_detected=     req.metrics_summary.is_away_detected,
            ),
            raw_data=tuple(
                GazeRawFrame(
                    offset_ms= f.offset_ms,
                    confidence=f.confidence,
                    gaze=GazeVector(
                        left= GazeCoordinate(x=f.gaze.left.x,  y=f.gaze.left.y),
                        right=GazeCoordinate(x=f.gaze.right.x, y=f.gaze.right.y),
                    ),
                    head=HeadPose(
                        pitch=f.head.pitch,
                        yaw=  f.head.yaw,
                        roll= f.head.roll,
                    ),
                )
                for f in req.raw_data
            ),
            events=tuple(
                GazeEvent(
                    type=     GazeEventType(e.type),
                    offset_ms=e.offset_ms,
                    direction=GazeDirection(e.direction),
                )
                for e in req.events
            ),
        )