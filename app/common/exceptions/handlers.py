import logging
import uuid
from typing import Any
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.common.exceptions.custom_exceptions import AppBaseException

logger = logging.getLogger("uvicorn.error")

def create_error_response(status_code: int, message: str, errors: Any = None):
    return JSONResponse(
        status_code=status_code,
        content={
            "data": None,
            "isSuccess": False,
            "message": message,
            "httpStatusCode": status_code,
            "errors": errors,
            "applogs": None,
            "logTraceId": str(uuid.uuid4())
        },
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation failed for the request data.",
        errors=exc.errors()
    )

async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    logger.error(f"Response data mismatch: {str(exc)}")
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="The server returned data that doesn't match the expected format.",
        errors=str(exc)
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail
    )

async def app_base_exception_handler(request: Request, exc: AppBaseException):
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server error")
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An internal server error occurred. Please contact support."
    )

def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ResponseValidationError, response_validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(AppBaseException, app_base_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
