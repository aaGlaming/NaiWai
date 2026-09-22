from pydantic import BaseModel


class ImageOut(BaseModel):
    id: int
    filename: str
    title: str | None = None
    category: str
    extension: str
    rarity: str
    favorite_count: int
    download_count: int
    url: str


class ImageListOut(BaseModel):
    images: list[ImageOut]
    total: int
    page: int
