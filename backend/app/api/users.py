from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Achievement, Image, User, UserAchievement, UserCollection, UserFavorite
from app.schemas import LocalDataImportRequest, UserEventRequest
from app.services.user_data import ensure_stats, evaluate_achievements, serialize_user_data

router = APIRouter(prefix="/me")


def find_image(db: Session, filename: str) -> Image:
    image = db.scalar(select(Image).where(Image.filename == filename, Image.is_active.is_(True)))
    if image is None:
        raise HTTPException(status_code=404, detail="图片不存在")
    return image


@router.get("/data")
def get_my_data(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return serialize_user_data(db, user)


@router.put("/favorites/{filename}")
def add_favorite(filename: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    image = find_image(db, filename)
    if db.get(UserFavorite, (user.id, image.id)) is None:
        db.add(UserFavorite(user_id=user.id, image_id=image.id))
        image.favorite_count += 1
        db.flush()
        evaluate_achievements(db, user)
        db.commit()
    return {"success": True, "filename": filename}


@router.delete("/favorites/{filename}")
def remove_favorite(filename: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    image = find_image(db, filename)
    favorite = db.get(UserFavorite, (user.id, image.id))
    if favorite is not None:
        db.delete(favorite)
        image.favorite_count = max(0, image.favorite_count - 1)
        db.commit()
    return {"success": True, "filename": filename}


@router.put("/collection/{filename}")
def add_collection(filename: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    image = find_image(db, filename)
    item = db.scalar(select(UserCollection).where(
        UserCollection.user_id == user.id, UserCollection.image_id == image.id
    ))
    if item:
        item.obtain_count += 1
        item.last_obtained_at = datetime.now()
    else:
        db.add(UserCollection(user_id=user.id, image_id=image.id, source="draw"))
    db.flush()
    evaluate_achievements(db, user)
    db.commit()
    return {"success": True, "filename": filename}


@router.post("/import-local-data")
def import_local_data(payload: LocalDataImportRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.local_data_imported_at is not None:
        raise HTTPException(status_code=409, detail="本地数据已经导入过")
    filenames = set(payload.favorites) | set(payload.collection)
    image_map = {image.filename: image for image in db.scalars(
        select(Image).where(Image.filename.in_(filenames))
    ).all()} if filenames else {}
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
    achievement_map = {item.code: item for item in db.scalars(
        select(Achievement).where(Achievement.code.in_(codes))
    ).all()} if codes else {}
    achievement_ids = set(db.scalars(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)
    ).all())
    for achievement in achievement_map.values():
        if achievement.id not in achievement_ids:
            db.add(UserAchievement(user_id=user.id, achievement_id=achievement.id))
    stats = ensure_stats(db, user)
    stats.draws = max(stats.draws, payload.stats.draws)
    stats.ssr_count = max(stats.ssr_count, payload.stats.ssrCount)
    for name in ("wallpapers", "tarot", "quiz", "memes", "downloads", "matches", "streak"):
        setattr(stats, name, max(getattr(stats, name), getattr(payload.stats, name)))
    if payload.stats.lastCheckin > stats.last_checkin:
        stats.last_checkin = payload.stats.lastCheckin[:10]
    user.local_data_imported_at = datetime.now()
    db.flush()
    evaluate_achievements(db, user)
    db.commit()
    return {"success": True, "data": serialize_user_data(db, user)}


@router.post("/events")
def track_event(payload: UserEventRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stats = ensure_stats(db, user)
    fields = {
        "wallpaper": "wallpapers", "tarot": "tarot", "quiz": "quiz", "meme": "memes",
        "download": "downloads", "match": "matches",
    }
    if payload.event == "draw":
        stats.draws += payload.count
        stats.ssr_count += payload.ssr
    elif payload.event in fields:
        field = fields[payload.event]
        setattr(stats, field, getattr(stats, field) + payload.count)
    else:
        raise HTTPException(status_code=400, detail="不支持的统计事件")
    evaluate_achievements(db, user)
    db.commit()
    return {"success": True, "data": serialize_user_data(db, user)}
