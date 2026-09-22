from fastapi import Response

from app.core.config import get_settings

COOKIE_NAME = "access_token"
COOKIE_PATH = "/"
COOKIE_SAMESITE = "lax"


def set_auth_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )


def clear_auth_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        COOKIE_NAME,
        path=COOKIE_PATH,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=COOKIE_SAMESITE,
    )
