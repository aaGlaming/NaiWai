from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Achievement, Image, User, UserAchievement, UserCollection, UserFavorite, UserStats


STAT_FIELDS = ("draws", "wallpapers", "tarot", "quiz", "memes", "downloads", "matches", "streak")


def ensure_stats(db: Session, user: User) -> UserStats:
    stats = db.get(UserStats, user.id)
    if stats is None:
        stats = UserStats(user_id=user.id)
        db.add(stats)
        db.flush()
    return stats


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "email": user.email,
        "role": user.role,
        "local_data_imported": user.local_data_imported_at is not None,
    }


def serialize_user_data(db: Session, user: User) -> dict:
    stats = ensure_stats(db, user)
    favorites = db.scalars(
        select(Image.filename).join(UserFavorite, UserFavorite.image_id == Image.id)
        .where(UserFavorite.user_id == user.id).order_by(UserFavorite.created_at)
    ).all()
    collection = db.scalars(
        select(Image.filename).join(UserCollection, UserCollection.image_id == Image.id)
        .where(UserCollection.user_id == user.id).order_by(UserCollection.first_obtained_at)
    ).all()
    unlocked = db.scalars(
        select(Achievement.code).join(UserAchievement, UserAchievement.achievement_id == Achievement.id)
        .where(UserAchievement.user_id == user.id).order_by(UserAchievement.unlocked_at)
    ).all()
    return {
        "favorites": list(favorites),
        "collection": list(collection),
        "unlocked": list(unlocked),
        "stats": {
            "draws": stats.draws,
            "ssrCount": stats.ssr_count,
            "wallpapers": stats.wallpapers,
            "tarot": stats.tarot,
            "quiz": stats.quiz,
            "memes": stats.memes,
            "downloads": stats.downloads,
            "matches": stats.matches,
            "streak": stats.streak,
            "lastCheckin": stats.last_checkin,
        },
    }


def evaluate_achievements(db: Session, user: User) -> None:
    stats = ensure_stats(db, user)
    values = {
        "favorites": db.scalar(select(func.count()).select_from(UserFavorite).where(UserFavorite.user_id == user.id)) or 0,
        "collection": db.scalar(select(func.count()).select_from(UserCollection).where(UserCollection.user_id == user.id)) or 0,
        "draws": stats.draws,
        "ssr_count": stats.ssr_count,
        "wallpapers": stats.wallpapers,
        "tarot": stats.tarot,
        "quiz": stats.quiz,
        "memes": stats.memes,
        "matches": stats.matches,
        "streak": stats.streak,
    }
    unlocked = set(db.scalars(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)
    ).all())
    for achievement in db.scalars(select(Achievement).where(Achievement.is_active.is_(True))).all():
        if achievement.id not in unlocked and values.get(achievement.condition_type, 0) >= achievement.condition_value:
            db.add(UserAchievement(user_id=user.id, achievement_id=achievement.id))
