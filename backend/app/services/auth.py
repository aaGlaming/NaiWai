import logging

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.datetime import utc_now_naive
from app.core.enums import UserRole, UserStatus
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_helpers import ensure_stats

logger = logging.getLogger(__name__)

DESKTOP_USERNAME = "local"


def register_user(db: Session, payload: RegisterRequest) -> User:
    duplicate_checks = [User.username == payload.username]
    if payload.email:
        duplicate_checks.append(User.email == str(payload.email))
    existing = db.scalar(select(User).where(or_(*duplicate_checks)))
    if existing:
        raise ConflictError("用户名或邮箱已存在")
    user = User(
        username=payload.username,
        email=str(payload.email) if payload.email else None,
        nickname=payload.nickname,
        password_hash=hash_password(payload.password),
        role=UserRole.USER.value,
        status=UserStatus.ACTIVE.value,
    )
    db.add(user)
    db.flush()
    ensure_stats(db, user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: LoginRequest) -> User:
    user = db.scalar(select(User).where(or_(User.username == payload.username, User.email == payload.username)))
    if not user or not verify_password(payload.password, user.password_hash):
        logger.info("login failed for identifier=%s", payload.username)
        raise UnauthorizedError("用户名或密码错误")
    if user.status != UserStatus.ACTIVE.value:
        raise ForbiddenError("账号不可用")
    user.last_login_at = utc_now_naive()
    db.commit()
    db.refresh(user)
    return user


def ensure_desktop_user(db: Session, desktop_mode: bool) -> User:
    if not desktop_mode:
        raise NotFoundError("Not found")
    user = db.scalar(select(User).where(User.username == DESKTOP_USERNAME))
    if user is None:
        user = User(
            username=DESKTOP_USERNAME,
            nickname="本地奶蛙",
            email=None,
            password_hash=hash_password("desktop-local-account"),
            local_data_imported_at=utc_now_naive(),
            role=UserRole.USER.value,
            status=UserStatus.ACTIVE.value,
        )
        db.add(user)
        db.flush()
        ensure_stats(db, user)
        db.commit()
        db.refresh(user)
    return user
