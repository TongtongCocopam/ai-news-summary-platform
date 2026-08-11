import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, TimeoutError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.response import ApiResponse
from app.exceptions.base import AppException
from app.exceptions.error_code import ErrorCode


logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ):
        error = exc.error_code

        response = ApiResponse.error_response(
            code=error.code,
            message=error.message,
            details=exc.details,
        )

        return JSONResponse(
            status_code=error.status.value,
            content=jsonable_encoder(response),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        error = ErrorCode.VALIDATION_ERROR

        details = [
            {
                "field": ".".join(
                    str(value) for value in item["loc"]
                ),
                "message": item["msg"],
            }
            for item in exc.errors()
        ]

        response = ApiResponse.error_response(
            code=error.code,
            message=error.message,
            details=details,
        )

        return JSONResponse(
            status_code=error.status.value,
            content=jsonable_encoder(response),
        )

    @app.exception_handler(
        (OperationalError, TimeoutError)
    )
    async def database_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.exception("Database connection error")

        error = ErrorCode.DATABASE_UNAVAILABLE

        response = ApiResponse.error_response(
            code=error.code,
            message=error.message,
        )

        return JSONResponse(
            status_code=error.status.value,
            content=jsonable_encoder(response),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):
        response = ApiResponse.error_response(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(response),
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.exception("Unhandled exception")

        error = ErrorCode.INTERNAL_SERVER_ERROR

        response = ApiResponse.error_response(
            code=error.code,
            message=error.message,
        )

        return JSONResponse(
            status_code=error.status.value,
            content=jsonable_encoder(response),
        )