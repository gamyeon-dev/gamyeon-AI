# app/report/infrastructure/webhook_callback_adapter.py
from app.report.application.port.callback_port import CallbackPort
from app.report.schema.response import ReportCallbackPayload
from app.core.webhook.webhook_sender import WebhookSender

class WebhookCallbackAdapter(CallbackPort):

    def __init__(self, sender: WebhookSender) -> None:
        self._sender = sender

    async def send(self, url: str, payload: ReportCallbackPayload) -> None:
        await self._sender.send(
            url=url,
            payload=payload.model_dump(by_alias=True),  # camelCase 직렬화
            target="spring_webhook",
        )
