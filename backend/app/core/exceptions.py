from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 400

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class BadRequestError(AppError):
    status_code = 400


class UnauthorizedError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class RateLimitError(AppError):
    status_code = 429


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
