from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Achievement, User, UserAchievement, UserCollection, UserFavorite
from app.services.auth_helpers import ensure_stats


def evaluate_achievements(db: Session, user: User) -> None:
    stats = ensure_stats(db, user)
    values = {
        "favorites": db.scalar(select(func.count()).select_from(UserFavorite).where(UserFavorite.user_id == user.id))
        or 0,
        "collection": db.scalar(
            select(func.count()).select_from(UserCollection).where(UserCollection.user_id == user.id)
        )
        or 0,
        "draws": stats.draws,
        "ssr_count": stats.ssr_count,
        "wallpapers": stats.wallpapers,
        "tarot": stats.tarot,
        "quiz": stats.quiz,
        "memes": stats.memes,
        "matches": stats.matches,
        "streak": stats.streak,
        "daily_draws": 1 if stats.last_daily_draw else 0,
    }
    unlocked = set(db.scalars(select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)).all())
    for achievement in db.scalars(select(Achievement).where(Achievement.is_active.is_(True))).all():
        if achievement.id not in unlocked and values.get(achievement.condition_type, 0) >= achievement.condition_value:
            db.add(UserAchievement(user_id=user.id, achievement_id=achievement.id))
