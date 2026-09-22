from sqlalchemy.orm import Session

from app.models import User, UserStats
from app.schemas.auth import UserResponse


def ensure_stats(db: Session, user: User) -> UserStats:
    stats = db.get(UserStats, user.id)
    if stats is None:
        stats = UserStats(user_id=user.id)
        db.add(stats)
        db.flush()
    return stats


def user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        role=user.role,
        local_data_imported=user.local_data_imported_at is not None,
    )
