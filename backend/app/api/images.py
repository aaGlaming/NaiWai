from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.image import ImageListOut, ImageOut
from app.services.images import get_active_image, image_to_out, list_images

router = APIRouter()


@router.get("/images", response_model=ImageListOut)
def get_images(
    category: str | None = None,
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(500, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ImageListOut:
    return list_images(db, category=category, q=q, page=page, page_size=page_size)


@router.get("/images/{filename}", response_model=ImageOut)
def get_image(filename: str, db: Session = Depends(get_db)) -> ImageOut:
    return image_to_out(get_active_image(db, filename))
