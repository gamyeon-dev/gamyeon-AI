from langchain_openai import ChatOpenAI

from app.core.webhook.webhook_sender import WebhookSender
from app.feedback.infrastructure.langchain_feedback_adapter import LangchainFeedbackAdapter
from app.feedback.infrastructure.prompt_provider import FeedbackPromptProvider
from app.feedback.infrastructure.webhook_callback_adapter import FeedbackWebhookCallbackAdapter
from app.feedback.application.service import FeedbackService


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.0)


def get_feedback_service() -> FeedbackService:
    port = LangchainFeedbackAdapter(          # ← FeedbackAdapter → LangchainFeedbackAdapter
        llm=_get_llm(),
        prompt_provider=FeedbackPromptProvider(),
    )
    sender = WebhookSender()
    callback = FeedbackWebhookCallbackAdapter(sender)
    return FeedbackService(feedback_port=port, callback=callback)
