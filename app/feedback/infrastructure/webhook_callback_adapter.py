# feedback/infrastructure/webhook_callback_adapter.py
from app.core.webhook.webhook_sender import WebhookSender
from app.feedback.application.port.callback_port import FeedbackCallbackPort
from app.feedback.schema.response import FeedbackResponse

class FeedbackWebhookCallbackAdapter(FeedbackCallbackPort):

    def __init__(self, sender: WebhookSender) -> None:
        self._sender = sender

    async def send(self, url: str, payload: FeedbackResponse) -> None:
        await self._sender.send(
            url=url,
            payload=payload.model_dump(by_alias=True),  # camelCase 직렬화
            target="spring_webhook_feedback"
        )
