from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app.core.enums import UserStatus
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.database import get_db
from app.models import User


def get_optional_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    if not access_token:
        return None
    user_id = decode_access_token(access_token)
    if user_id is None:
        return None
    return db.get(User, user_id)


def get_current_user(user: User | None = Depends(get_optional_user)) -> User:
    if user is None or user.status != UserStatus.ACTIVE.value:
        raise UnauthorizedError("请先登录")
    return user
