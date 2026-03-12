from __future__ import annotations
from typing import Literal, Generic, TypeVar, Optional
from pydantic import BaseModel


T = TypeVar("T")

# API 동기 응답 공통 래퍼
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    code:    str
    message: str
    data:    Optional[T] = None

class QuestionCallbackPayload(BaseModel):
    intvId:       int
    status:       Literal["SUCCESS", "FAILED"]
    questions:    list[str]
    errorMessage: str | None = None
