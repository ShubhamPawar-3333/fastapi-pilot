"""Custom exception classes and global error handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = 500,
        detail: str | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(
        self, resource: str = "Resource", detail: str | None = None
    ) -> None:
        super().__init__(
            message=f"{resource} not found", status_code=404, detail=detail
        )


class BadRequestException(AppException):
    """Invalid client request."""

    def __init__(
        self, message: str = "Bad request", detail: str | None = None
    ) -> None:
        super().__init__(message=message, status_code=400, detail=detail)


class UnauthorizedException(AppException):
    """Authentication required."""

    def __init__(
        self, message: str = "Unauthorized", detail: str | None = None
    ) -> None:
        super().__init__(message=message, status_code=401, detail=detail)


class ForbiddenException(AppException):
    """Insufficient permissions."""

    def __init__(
        self, message: str = "Forbidden", detail: str | None = None
    ) -> None:
        super().__init__(message=message, status_code=403, detail=detail)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "detail": exc.detail,
            },
        )