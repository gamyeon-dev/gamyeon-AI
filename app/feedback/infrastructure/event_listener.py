# app/feedback/infrastructure/event_listener.py
import logging

from app.core.events import bus
from app.core.events.signals import media_completed
from app.feedback.application.service import FeedbackService

logger = logging.getLogger(__name__)


def register_feedback_listeners(service: FeedbackService) -> None:
    bus.subscribe(media_completed, service.media_completed)
    logger.info("feedback 이벤트 리스너 등록 완료")
