from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.errors import ErrorResponse

logger = logging.getLogger(__name__)


def _status_code_to_error(code: int) -> str:
    mapping: Dict[int, str] = {
        HTTPStatus.BAD_REQUEST: "bad_request",
        HTTPStatus.UNAUTHORIZED: "unauthorized",
        HTTPStatus.FORBIDDEN: "forbidden",
        HTTPStatus.NOT_FOUND: "not_found",
        HTTPStatus.UNPROCESSABLE_ENTITY: "validation_error",
        HTTPStatus.BAD_GATEWAY: "bad_gateway",
        HTTPStatus.SERVICE_UNAVAILABLE: "service_unavailable",
        HTTPStatus.GATEWAY_TIMEOUT: "gateway_timeout",
        HTTPStatus.INTERNAL_SERVER_ERROR: "internal_error",
    }
    return mapping.get(code, "error")


async def http_exception_handler(request: Request, exc: Exception) -> Response:
    # Note: FastAPI's HTTPException.detail can be any value; prefer string message
    if isinstance(exc, HTTPException):
        message = exc.detail if isinstance(exc.detail, str) else HTTPStatus(exc.status_code).phrase
        payload = ErrorResponse(
            error=_status_code_to_error(exc.status_code),
            message=message,
            details=None,
        ).model_dump()
        return JSONResponse(status_code=exc.status_code, content=payload)
    # Fallback (should not happen as this handler is registered for HTTPException)
    logger.exception("Unexpected exception in http_exception_handler", exc_info=exc)
    payload = ErrorResponse(
        error="internal_error",
        message="Internal Server Error",
        details=None,
    ).model_dump()
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content=payload)


async def validation_exception_handler(request: Request, exc: Exception) -> Response:
    # Do not log as error; it's a client issue
    if isinstance(exc, RequestValidationError):
        payload = ErrorResponse(
            error="validation_error",
            message="Validation error",
            details={"errors": exc.errors()},
        ).model_dump()
        return JSONResponse(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, content=payload)
    logger.exception("Unexpected exception in validation_exception_handler", exc_info=exc)
    payload = ErrorResponse(
        error="internal_error",
        message="Internal Server Error",
        details=None,
    ).model_dump()
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content=payload)


async def httpx_exception_handler(request: Request, exc: Exception) -> Response:
    # Upstream service/network error; log as warning/error depending on severity
    if isinstance(exc, httpx.HTTPError):
        logger.error("Upstream HTTP error: %s", str(exc), exc_info=exc)
        payload = ErrorResponse(
            error="bad_gateway",
            message="Upstream service error",
            details=None,
        ).model_dump()
        return JSONResponse(status_code=HTTPStatus.BAD_GATEWAY, content=payload)
    logger.exception("Unexpected exception in httpx_exception_handler", exc_info=exc)
    payload = ErrorResponse(
        error="internal_error",
        message="Internal Server Error",
        details=None,
    ).model_dump()
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content=payload)


async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    logger.exception("Unhandled server error", exc_info=exc)
    payload = ErrorResponse(
        error="internal_error",
        message="Internal Server Error",
        details=None,
    ).model_dump()
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content=payload)


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers for consistent error responses."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(httpx.HTTPError, httpx_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
