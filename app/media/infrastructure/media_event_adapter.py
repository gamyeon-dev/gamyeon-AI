from __future__ import annotations

import logging

from app.core.events import bus, signals

from app.media.application.port.media_event_port        import MediaEventPort
from app.media.domain.pipeline.media_processing_result  import MediaProcessingResult

logger = logging.getLogger(__name__)


class MediaEventAdapter(MediaEventPort):
    """
    MediaEventPort 구현체

    blinker Signal 기반 내부 이벤트 발행(현재는 Feedback에만)
    """

    def publish_completed(self, result: MediaProcessingResult) -> None:
        bus.emit(
            signal= signals.media_completed,
            payload=result.to_feedback_event_payload(),
            sender= "media",
        )
        logger.info(
            "media_completed 이벤트 발행 interview_id=%s question_id=%s",
            result.interview_id, result.question_id,
        )