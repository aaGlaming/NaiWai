from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Image
from app.schemas.image import ImageListOut, ImageOut


def escape_like(value: str) -> str:
    return value.replace("/", "//").replace("%", "/%").replace("_", "/_")


def image_to_out(image: Image) -> ImageOut:
    return ImageOut(
        id=image.id,
        filename=image.filename,
        title=image.title,
        category=image.category,
        extension=image.extension,
        rarity=image.rarity,
        favorite_count=image.favorite_count,
        download_count=image.download_count,
        url=f"/images/{image.filename}",
    )


def get_active_image(db: Session, filename: str) -> Image:
    image = db.scalar(select(Image).where(Image.filename == filename, Image.is_active.is_(True)))
    if image is None:
        raise NotFoundError("图片不存在")
    return image


def list_images(
    db: Session,
    category: str | None = None,
    q: str | None = None,
    page: int = 1,
    page_size: int = 500,
) -> ImageListOut:
    filters = [Image.is_active.is_(True)]
    if category and category != "all":
        filters.append(Image.category == category)
    if q:
        filters.append(Image.filename.like(f"%{escape_like(q)}%", escape="/"))
    total = db.scalar(select(func.count()).select_from(Image).where(*filters)) or 0
    images = db.scalars(
        select(Image)
        .where(*filters)
        .order_by(Image.sort_order, Image.filename)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return ImageListOut(images=[image_to_out(image) for image in images], total=total, page=page)
