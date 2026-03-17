from app.question.application.port.callback_port import CallbackPort
from app.question.schema.response import QuestionCallbackPayload
from app.core.webhook.webhook_sender import WebhookSender

TARGET = "spring_webhook"


class WebhookCallbackAdapter(CallbackPort):

    def __init__(self, sender: WebhookSender) -> None:
        self._sender = sender

    async def send(self, url: str, payload: QuestionCallbackPayload) -> None:
        await self._sender.send(
            url=     url,
            payload= payload.model_dump(by_alias=True),
            target=  TARGET,
        )
