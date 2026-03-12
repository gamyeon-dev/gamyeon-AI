from pathlib import Path
from langchain_openai import ChatOpenAI
from app.feedback.application.service import FeedbackService
from app.feedback.infrastructure.langchain_feedback_adapter import LangchainFeedbackAdapter
from app.feedback.infrastructure.prompt_provider import FeedbackPromptProvider


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
        #api_key="invalid-key-for-test",
        #infrastructure/di.py 임시 수정
    )
    
def get_feedback_service() -> FeedbackService:
    llm             = _get_llm()
    prompt_provider = FeedbackPromptProvider(version="v1")   # 버전 교체는 이 한 줄
    adapter         = LangchainFeedbackAdapter(llm=llm, prompt_provider=prompt_provider)
    return FeedbackService(feedback_port=adapter)
