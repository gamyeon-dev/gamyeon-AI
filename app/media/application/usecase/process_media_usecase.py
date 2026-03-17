from __future__ import annotations

import logging

from core.exceptions import STTTranscriptionError

from media.application.service          import MediaService, ProcessMediaCommand
from media.application.port             import ResultWebhookPort, MediaEventPort

logger = logging.getLogger(__name__)


class ProcessMediaUseCase:
    
    """
    미디어 처리 파이프라인 유즈케이스

    의존성:
    - 모든 외부 연동은 포트(인터페이스)에만 의존
    - 구체 구현(WebhookSender, blinker 등) 직접 참조 없음

    인바운드:
        ProcessMediaCommand (interface/mapper에서 생성)

    아웃바운드 포트:
        ResultWebhookPort  → SpringWebhookAdapter (infrastructure)
        MediaEventPort     → MediaEventAdapter    (infrastructure)

    router.py에서 BackgroundTasks로 실행:
    background_tasks.add_task(use_case.execute, command)
    """

    def __init__(
        self,
        service:        MediaService,
        webhook_port:   ResultWebhookPort,
        event_port:     MediaEventPort,
    ) -> None:
        self._service  = service
        self._webhook  = webhook_port
        self._event    = event_port

    async def execute(self, command: ProcessMediaCommand) -> None:
        """
        유즈케이스 실행.

        성공 (DONE):
        1. ResultWebhookPort.send_success() → Spring Boot
        2. MediaEventPort.publish_completed() → feedback 도메인

        STT 실패 (FAILED):
        1. ResultWebhookPort.send_failed() → Spring Boot
        2. 이벤트 미발행

        예상치 못한 실패: critical 로깅 후 종료
        """
        try:
            result = await self._service.process(command)

            await self._webhook.send_success(result)
            self._event.publish_completed(result)

            logger.info(
                "파이프라인 완료 interview_id=%s question_id=%s degraded=%s",
                command.interview_id, command.question_id, result.degraded,
            )

        except STTTranscriptionError as e:
            logger.error(
                "STT 실패 FAILED 처리 "
                "interview_id=%s question_id=%s error=%s",
                command.interview_id, command.question_id, e,
            )
            await self._webhook.send_failed(
                interview_id=command.interview_id,
                question_id= command.question_id,
                error_code=  "STT_TRANSCRIPTION_FAILED",
                message=     str(e),
            )

        except Exception as e:
            logger.critical(
                "파이프라인 예상치 못한 실패 "
                "interview_id=%s question_id=%s error=%s",
                command.interview_id, command.question_id, e,
                exc_info=True,
            )