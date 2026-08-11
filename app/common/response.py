from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: object | None = None


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: ErrorResponse | None = None

    @classmethod
    def success_response(cls, data: T | None = None):
        return cls(
            success=True,
            data=data,
            error=None,
        )

    @classmethod
    def error_response(
        cls,
        code: str,
        message: str,
        details: object | None = None,
    ):
        return cls(
            success=False,
            data=None,
            error=ErrorResponse(
                code=code,
                message=message,
                details=details,
            ),
        )