from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Image

router = APIRouter()


def serialize_image(image: Image) -> dict:
    return {"id": image.id, "filename": image.filename, "title": image.title, "category": image.category,
            "extension": image.extension, "rarity": image.rarity, "favorite_count": image.favorite_count,
            "download_count": image.download_count, "url": f"/images/{image.filename}"}


@router.get("/images")
def get_images(category: str | None = None, q: str | None = None, page: int = Query(1, ge=1),
               page_size: int = Query(500, ge=1, le=500), db: Session = Depends(get_db)):
    filters = [Image.is_active.is_(True)]
    if category and category != "all":
        filters.append(Image.category == category)
    if q:
        filters.append(Image.filename.like(f"%{q}%"))
    total = db.scalar(select(func.count()).select_from(Image).where(*filters)) or 0
    images = db.scalars(select(Image).where(*filters).order_by(Image.sort_order, Image.filename)
                        .offset((page - 1) * page_size).limit(page_size)).all()
    return {"images": [serialize_image(image) for image in images], "total": total, "page": page}


@router.get("/images/{filename}")
def get_image(filename: str, db: Session = Depends(get_db)):
    image = db.scalar(select(Image).where(Image.filename == filename, Image.is_active.is_(True)))
    if image is None:
        raise HTTPException(status_code=404, detail="图片不存在")
    return serialize_image(image)
