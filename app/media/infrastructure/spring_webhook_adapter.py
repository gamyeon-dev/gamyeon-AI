from __future__ import annotations

import logging

from app.core.webhook import WebhookSender, RetryPolicy
from app.core.config  import settings

from app.media.application.port.result_webhook_port    import ResultWebhookPort
from app.media.domain.pipeline.media_processing_result import MediaProcessingResult
from app.media.interface.schema.webhook                import WebhookFailedPayload

logger = logging.getLogger(__name__)


class SpringWebhookAdapter(ResultWebhookPort):
    """
    ResultWebhookPort 구현체

    WebhookSender 기반 Spring Boot 결과 전송
    """
    def __init__(self, policy: RetryPolicy | None = None) -> None:
        self._sender = WebhookSender(policy = policy or RetryPolicy())

    async def send_success(self, result: MediaProcessingResult) -> None:
        """
        성공시 전송

        args:
            MediaProcessingResult: Media 프로세싱 결과
        """
        await self._sender.send(
            url=    settings.SPRING_WEBHOOK_URL,
            payload=result.to_spring_webhook_payload().model_dump(by_alias=True),
            target= "spring_webhook",
        )
        logger.info(
            "Webhook 전송 완료 (DONE) interview_id=%s question_id=%s",
            result.interview_id, result.question_id,
        )

    async def send_failed(
        self,
        interview_id: int,
        question_id:  int,
        error_code:   str,
        message:      str,
    ) -> None:
        """
        실패시 전송

        args:
            interview_id: 면접 ID
            question_id:  질문 ID
            error_code:   에러 코드
            message:      에러 상세 메세지
        
        """
        await self._sender.send(
            url=    settings.SPRING_WEBHOOK_URL,
            payload=WebhookFailedPayload(
                interviewId=interview_id,
                questionId= question_id,
                errorCode=  error_code,
                message=    message,
            ).model_dump(by_alias=True),
            target= "spring_webhook_failed",
        )
        logger.info(
            "Webhook 전송 완료 (FAILED) interview_id=%s question_id=%s",
            interview_id, question_id,
        )