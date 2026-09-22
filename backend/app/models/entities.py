from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

ID_TYPE = BigInteger().with_variant(Integer, "sqlite")


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[str] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(20), default="user", index=True)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    local_data_imported_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    stats: Mapped["UserStats"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)


class Image(Base, TimestampMixin):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(20), index=True)
    extension: Mapped[str] = mapped_column(String(10))
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    rarity: Mapped[str] = mapped_column(String(10), default="N", index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    view_count: Mapped[int] = mapped_column(BigInteger, default=0)
    favorite_count: Mapped[int] = mapped_column(BigInteger, default=0)
    download_count: Mapped[int] = mapped_column(BigInteger, default=0)


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)


class ImageTag(Base):
    __tablename__ = "image_tags"

    image_id: Mapped[int] = mapped_column(ForeignKey("images.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class UserFavorite(Base):
    __tablename__ = "user_favorites"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class UserCollection(Base):
    __tablename__ = "user_collection"
    __table_args__ = (UniqueConstraint("user_id", "image_id", name="uq_collection_user_image"),)

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id", ondelete="CASCADE"), index=True)
    obtain_count: Mapped[int] = mapped_column(Integer, default=1)
    source: Mapped[str] = mapped_column(String(20), default="draw")
    first_obtained_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_obtained_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class UserStats(Base):
    __tablename__ = "user_stats"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    draws: Mapped[int] = mapped_column(Integer, default=0)
    ssr_count: Mapped[int] = mapped_column(Integer, default=0)
    wallpapers: Mapped[int] = mapped_column(Integer, default=0)
    tarot: Mapped[int] = mapped_column(Integer, default=0)
    quiz: Mapped[int] = mapped_column(Integer, default=0)
    memes: Mapped[int] = mapped_column(Integer, default=0)
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    matches: Mapped[int] = mapped_column(Integer, default=0)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_checkin: Mapped[str] = mapped_column(String(10), default="")
    pity_count: Mapped[int] = mapped_column(Integer, default=0)
    last_daily_draw: Mapped[str] = mapped_column(String(10), default="")
    mines: Mapped[int] = mapped_column(Integer, default=0)
    last_daily_mine: Mapped[str] = mapped_column(String(10), default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(back_populates="stats")


class Achievement(Base, TimestampMixin):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    icon: Mapped[str | None] = mapped_column(String(255), nullable=True)
    condition_type: Mapped[str] = mapped_column(String(50))
    condition_value: Mapped[int] = mapped_column(Integer)
    points: Mapped[int] = mapped_column(Integer, default=10)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    achievement_id: Mapped[int] = mapped_column(ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ContactMessage(Base, TimestampMixin):
    __tablename__ = "contact_messages"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(150))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="unread", index=True)
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
