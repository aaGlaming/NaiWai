from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.datetime import utc_now_naive
from app.core.enums import EVENT_COUNTER_FIELDS, UserEvent
from app.core.exceptions import BadRequestError, ConflictError
from app.models import (
    Achievement,
    Image,
    User,
    UserAchievement,
    UserCollection,
    UserFavorite,
    UserStats,
)
from app.schemas.user import LocalDataImportRequest, LocalStats, UserDataOut, UserEventRequest
from app.services.achievements import evaluate_achievements
from app.services.auth_helpers import ensure_stats
from app.services.images import get_active_image

MAX_STATS_FIELDS = (
    "draws",
    "ssr_count",
    "wallpapers",
    "tarot",
    "quiz",
    "memes",
    "downloads",
    "matches",
    "streak",
    "pity_count",
)


def stats_to_out(stats: UserStats) -> LocalStats:
    return LocalStats(
        draws=stats.draws,
        ssrCount=stats.ssr_count,
        wallpapers=stats.wallpapers,
        tarot=stats.tarot,
        quiz=stats.quiz,
        memes=stats.memes,
        downloads=stats.downloads,
        matches=stats.matches,
        streak=stats.streak,
        lastCheckin=stats.last_checkin,
        pityCount=stats.pity_count,
        lastDailyDraw=stats.last_daily_draw,
    )


def serialize_user_data(db: Session, user: User) -> UserDataOut:
    stats = ensure_stats(db, user)
    favorites = db.scalars(
        select(Image.filename)
        .join(UserFavorite, UserFavorite.image_id == Image.id)
        .where(UserFavorite.user_id == user.id)
        .order_by(UserFavorite.created_at)
    ).all()
    collection = db.scalars(
        select(Image.filename)
        .join(UserCollection, UserCollection.image_id == Image.id)
        .where(UserCollection.user_id == user.id)
        .order_by(UserCollection.first_obtained_at)
    ).all()
    unlocked = db.scalars(
        select(Achievement.code)
        .join(UserAchievement, UserAchievement.achievement_id == Achievement.id)
        .where(UserAchievement.user_id == user.id)
        .order_by(UserAchievement.unlocked_at)
    ).all()
    return UserDataOut(
        favorites=list(favorites),
        collection=list(collection),
        unlocked=list(unlocked),
        stats=stats_to_out(stats),
    )


def add_favorite(db: Session, user: User, filename: str) -> None:
    image = get_active_image(db, filename)
    if db.get(UserFavorite, (user.id, image.id)) is None:
        db.add(UserFavorite(user_id=user.id, image_id=image.id))
        image.favorite_count += 1
        db.flush()
        evaluate_achievements(db, user)
        db.commit()


def remove_favorite(db: Session, user: User, filename: str) -> None:
    image = get_active_image(db, filename)
    favorite = db.get(UserFavorite, (user.id, image.id))
    if favorite is not None:
        db.delete(favorite)
        image.favorite_count = max(0, image.favorite_count - 1)
        db.commit()


def add_collection(db: Session, user: User, filename: str) -> None:
    image = get_active_image(db, filename)
    item = db.scalar(
        select(UserCollection).where(UserCollection.user_id == user.id, UserCollection.image_id == image.id)
    )
    if item:
        item.obtain_count += 1
        item.last_obtained_at = utc_now_naive()
    else:
        db.add(UserCollection(user_id=user.id, image_id=image.id, source="draw"))
    db.flush()
    evaluate_achievements(db, user)
    db.commit()


def _merge_local_stats(stats: UserStats, payload: LocalStats) -> None:
    incoming = {
        "draws": payload.draws,
        "ssr_count": payload.ssrCount,
        "wallpapers": payload.wallpapers,
        "tarot": payload.tarot,
        "quiz": payload.quiz,
        "memes": payload.memes,
        "downloads": payload.downloads,
        "matches": payload.matches,
        "streak": payload.streak,
        "pity_count": payload.pityCount,
    }
    for field in MAX_STATS_FIELDS:
        setattr(stats, field, max(getattr(stats, field), incoming[field]))
    if payload.lastCheckin > stats.last_checkin:
        stats.last_checkin = payload.lastCheckin[:10]
    if payload.lastDailyDraw > stats.last_daily_draw:
        stats.last_daily_draw = payload.lastDailyDraw[:10]


def import_local_data(db: Session, user: User, payload: LocalDataImportRequest) -> UserDataOut:
    if user.local_data_imported_at is not None:
        raise ConflictError("本地数据已经导入过")
    filenames = set(payload.favorites) | set(payload.collection)
    image_map = (
        {image.filename: image for image in db.scalars(select(Image).where(Image.filename.in_(filenames))).all()}
        if filenames
        else {}
    )
    favorite_ids = set(db.scalars(select(UserFavorite.image_id).where(UserFavorite.user_id == user.id)).all())
    for filename in set(payload.favorites):
        image = image_map.get(filename)
        if image and image.id not in favorite_ids:
            db.add(UserFavorite(user_id=user.id, image_id=image.id))
            image.favorite_count += 1
    collection_ids = set(db.scalars(select(UserCollection.image_id).where(UserCollection.user_id == user.id)).all())
    for filename in set(payload.collection):
        image = image_map.get(filename)
        if image and image.id not in collection_ids:
            db.add(UserCollection(user_id=user.id, image_id=image.id, source="migration"))
    codes = set(payload.unlocked)
    achievement_map = (
        {item.code: item for item in db.scalars(select(Achievement).where(Achievement.code.in_(codes))).all()}
        if codes
        else {}
    )
    achievement_ids = set(
        db.scalars(select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)).all()
    )
    for achievement in achievement_map.values():
        if achievement.id not in achievement_ids:
            db.add(UserAchievement(user_id=user.id, achievement_id=achievement.id))
    stats = ensure_stats(db, user)
    _merge_local_stats(stats, payload.stats)
    user.local_data_imported_at = utc_now_naive()
    db.flush()
    evaluate_achievements(db, user)
    db.commit()
    return serialize_user_data(db, user)


def track_event(db: Session, user: User, payload: UserEventRequest) -> UserDataOut:
    stats = ensure_stats(db, user)
    try:
        event = UserEvent(payload.event)
    except ValueError as exc:
        raise BadRequestError("不支持的统计事件") from exc
    if event is UserEvent.DRAW:
        stats.draws += payload.count
        stats.ssr_count += payload.ssr
        stats.pity_count = payload.pity
    elif event is UserEvent.CHECKIN:
        today = date.today().isoformat()
        if stats.last_checkin != today:
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            stats.streak = stats.streak + 1 if stats.last_checkin == yesterday else 1
            stats.last_checkin = today
    elif event is UserEvent.DAILY_DRAW:
        today = date.today().isoformat()
        if stats.last_daily_draw != today:
            stats.last_daily_draw = today
            stats.draws += payload.count
            stats.ssr_count += payload.ssr
        stats.pity_count = payload.pity
    elif event in EVENT_COUNTER_FIELDS:
        field = EVENT_COUNTER_FIELDS[event]
        setattr(stats, field, getattr(stats, field) + payload.count)
    else:
        raise BadRequestError("不支持的统计事件")
    evaluate_achievements(db, user)
    db.commit()
    return serialize_user_data(db, user)
