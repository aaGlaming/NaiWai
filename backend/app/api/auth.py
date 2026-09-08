from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, UserStats
from app.schemas import LoginRequest, RegisterRequest
from app.security import create_access_token, hash_password, verify_password
from app.services.user_data import serialize_user

router = APIRouter(prefix="/auth")


def set_auth_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        "access_token",
        token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    duplicate_checks = [User.username == payload.username]
    if payload.email:
        duplicate_checks.append(User.email == str(payload.email))
    existing = db.scalar(select(User).where(or_(*duplicate_checks)))
    if existing:
        raise HTTPException(status_code=409, detail="用户名或邮箱已存在")
    user = User(
        username=payload.username,
        email=str(payload.email) if payload.email else None,
        nickname=payload.nickname,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()
    db.add(UserStats(user_id=user.id))
    db.commit()
    set_auth_cookie(response, create_access_token(user.id))
    return {"user": serialize_user(user)}


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(or_(User.username == payload.username, User.email == payload.username)))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.status != "active":
        raise HTTPException(status_code=403, detail="账号不可用")
    user.last_login_at = datetime.now()
    db.commit()
    set_auth_cookie(response, create_access_token(user.id))
    return {"user": serialize_user(user)}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"success": True}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"user": serialize_user(user)}


@router.get("/desktop-login", include_in_schema=False)
def desktop_login(db: Session = Depends(get_db)):
    if not get_settings().desktop_mode:
        raise HTTPException(status_code=404, detail="Not found")
    user = db.scalar(select(User).where(User.username == "local"))
    if user is None:
        user = User(username="local", nickname="本地奶蛙", email=None,
                    password_hash=hash_password("desktop-local-account"),
                    local_data_imported_at=datetime.now())
        db.add(user)
        db.flush()
        db.add(UserStats(user_id=user.id))
        db.commit()
    response = RedirectResponse(url="/", status_code=302)
    set_auth_cookie(response, create_access_token(user.id))
    return response
