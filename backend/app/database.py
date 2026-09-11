from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _engine_options(database_url: str) -> dict:
    if not database_url.startswith("sqlite"):
        return {"pool_pre_ping": True, "pool_recycle": 1800}

    options: dict = {"connect_args": {"check_same_thread": False, "timeout": 30}}
    if ":memory:" in database_url:
        options["poolclass"] = StaticPool
        return options

    sqlite_path = database_url.removeprefix("sqlite:///")
    if sqlite_path and sqlite_path != ":memory:":
        Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    options["pool_pre_ping"] = True
    options["pool_recycle"] = 1800
    return options


database_url = get_settings().database_url
engine = create_engine(database_url, **_engine_options(database_url))

if database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def configure_sqlite(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        if ":memory:" not in database_url:
            cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
