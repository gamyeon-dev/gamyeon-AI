from abc import ABC, abstractmethod
from app.question.schema.response import QuestionCallbackPayload


class CallbackPort(ABC):

    @abstractmethod
    async def send(self, url: str, payload: QuestionCallbackPayload) -> None: ...
