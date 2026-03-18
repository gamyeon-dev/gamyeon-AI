# app/report/application/port/callback_port.py
from abc import ABC, abstractmethod
from app.report.schema.response import ReportCallbackPayload

class CallbackPort(ABC):

    @abstractmethod
    async def send(self, url: str, payload: ReportCallbackPayload) -> None:
        """Spring 콜백 엔드포인트로 결과 전송"""
        ...
