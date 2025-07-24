from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    status: str = "healthy"


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class RootResponse(BaseModel):
    message: str
    version: str
    status: str
