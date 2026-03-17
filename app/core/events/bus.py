"""
내부 이벤트 버스 추상화 레이어

blinker를 직접 노출하지 않음
emit / subscribe 인터페이스만 외부에 공개

MVP-2 전환 시:
- emit() 내부 구현만 교체(Kafka producer, Redis pub/sub 등)
- 도메인 코드 (emit/subscribe 호출부) 변경 없음

비동기 처리:
- blinker 자체는 동기 설계
- 핸들러가 코루틴인 경우 asyncio.create_task()로 래핑 → emit() 호출 즉시 반환 (non-blocking)→ 핸들러 실패가 emit() 호출자에 전파되지 않음
"""
from __future__ import annotations

import asyncio, logging
from typing import Any, Callable, Coroutine

from blinker import Signal

logger = logging.getLogger(__name__)

def emit(
    signal:  Signal,
    payload: dict[str, Any],
    sender:  str = "system"
) -> None:
    """
    이벤트 발행

    Args:
        signal:  발행할 Signal 객체 (signals.py에서 import)
        payload: 이벤트 데이터 (dict)
        sender:  발행 주체 식별자 (로깅용)

    Note:
        non-blocking. 핸들러는 백그라운드 태스크로 실행
        핸들러 예외는 로깅 후 무시 (발행자에게 전파 안 됨)
    """
    receivers = list(signal.receivers_for(signal))

    if not receivers:
        logger.debug(
            "이벤트 구독자 없음 signal=%s sender=%s",
            getattr(signal, "name", repr(signal)), sender,
        )
        return

    logger.debug(
        "이벤트 발행 signal=%s sender=%s receivers=%d",
        getattr(signal, "name", repr(signal)), sender, len(receivers),
    )

    for receiver in receivers:
        if asyncio.inspect.iscoroutinefunction(receiver):
            asyncio.create_task(
                _safe_call(receiver, payload, signal.name)
            )
        else:
            try:
                receiver(payload)
            except Exception as e:
                logger.error(
                    "동기 핸들러 실패 signal=%s receiver=%s error=%s",
                    getattr(signal, "name", repr(signal)), receiver.__name__, e,
                )


def subscribe(
    signal:  Signal,
    handler: Callable[..., Coroutine | None],
) -> None:
    """
    이벤트 구독 등록

    Args:
        signal:  구독할 Signal 객체
        handler: 이벤트 수신 시 호출될 핸들러
                동기/비동기 모두 지원

    사용 예:
        from app.core.events import bus
        from app.core.events.signals import media_completed
        from app.feedback.application.service import FeedbackService

        bus.subscribe(media_completed, feedback_service.on_media_completed)
    """
    signal.connect(handler)
    logger.debug(
        "이벤트 구독 등록 signal=%s handler=%s",
        getattr(signal, "name", repr(signal)),
        handler.__name__,
    )


async def _safe_call(
    handler:     Callable[..., Coroutine],
    payload:     dict[str, Any],
    signal_name: str,
) -> None:
    """비동기 핸들러 안전 실행. 예외 로깅 후 무시."""
    try:
        await handler(payload)
    except Exception as e:
        logger.error(
            "비동기 핸들러 실패 signal=%s handler=%s error=%s",
            signal_name, handler.__name__, e,
        )