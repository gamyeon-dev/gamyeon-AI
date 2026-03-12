
from pydantic import BaseModel
from typing import Generic, Optional, TypeVar

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    code:    str
    message: str
    data:    Optional[T] = None
