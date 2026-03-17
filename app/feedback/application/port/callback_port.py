# feedback/application/port/callback_port.py
from abc import ABC, abstractmethod
from app.feedback.schema.response import FeedbackResponse

class FeedbackCallbackPort(ABC):

    @abstractmethod
    async def send(self, url: str, payload: FeedbackResponse) -> None: ...
