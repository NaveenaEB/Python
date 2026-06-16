from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, Any
import uuid

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    isSuccess: bool
    message: str
    httpStatusCode: Optional[int] = None
    errors: Any = None
    applogs: Any = None
    logTraceId: str = Field(default_factory=lambda: str(uuid.uuid4()))