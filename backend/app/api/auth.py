from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.cookies import clear_auth_cookie, set_auth_cookie
from app.core.security import create_access_token
from app.database import get_db
from app.models import User
from app.schemas.auth import AuthUserOut, LoginRequest, RegisterRequest
from app.schemas.common import SuccessOut
from app.services.auth import authenticate_user, ensure_desktop_user, register_user
from app.services.auth_helpers import user_to_response

router = APIRouter(prefix="/auth")


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=AuthUserOut)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> AuthUserOut:
    user = register_user(db, payload)
    set_auth_cookie(response, create_access_token(user.id))
    return AuthUserOut(user=user_to_response(user))


@router.post("/login", response_model=AuthUserOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthUserOut:
    user = authenticate_user(db, payload)
    set_auth_cookie(response, create_access_token(user.id))
    return AuthUserOut(user=user_to_response(user))


@router.post("/logout", response_model=SuccessOut)
def logout(response: Response) -> SuccessOut:
    clear_auth_cookie(response)
    return SuccessOut()


@router.get("/me", response_model=AuthUserOut)
def me(user: User = Depends(get_current_user)) -> AuthUserOut:
    return AuthUserOut(user=user_to_response(user))


@router.get("/desktop-login", include_in_schema=False)
def desktop_login(db: Session = Depends(get_db)) -> RedirectResponse:
    user = ensure_desktop_user(db, get_settings().desktop_mode)
    response = RedirectResponse(url="/", status_code=302)
    set_auth_cookie(response, create_access_token(user.id))
    return response
