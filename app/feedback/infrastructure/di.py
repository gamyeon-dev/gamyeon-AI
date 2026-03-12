from functools import lru_cache
from fastapi import Depends
from langchain_openai import ChatOpenAI

from app.feedback.application.service import FeedbackService
from app.feedback.infrastructure.langchain_feedback_adapter import LangchainFeedbackAdapter


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,
        #api_key="invalid-key-for-test",
        # infrastructure/di.py 임시 수정
    )
    
    # infrastructure/di.py 임시 수정
def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,
        api_key="invalid-key-for-test",
    )



def get_feedback_service() -> FeedbackService:
    adapter = LangchainFeedbackAdapter(llm=_get_llm())
    return FeedbackService(feedback_port=adapter)
