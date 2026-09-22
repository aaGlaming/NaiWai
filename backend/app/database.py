from collections.abc import Generator
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

engine: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None


class Base(DeclarativeBase):
    pass


def _engine_options(database_url: str) -> dict[str, Any]:
    if not database_url.startswith("sqlite"):
        return {"pool_pre_ping": True, "pool_recycle": 1800}

    options: dict[str, Any] = {"connect_args": {"check_same_thread": False, "timeout": 30}}
    if ":memory:" in database_url:
        options["poolclass"] = StaticPool
        return options

    sqlite_path = database_url.removeprefix("sqlite:///")
    if sqlite_path and sqlite_path != ":memory:":
        Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    options["pool_pre_ping"] = True
    options["pool_recycle"] = 1800
    return options


def _configure_sqlite(database_url: str, db_engine: Engine) -> None:
    if not database_url.startswith("sqlite"):
        return

    @event.listens_for(db_engine, "connect")
    def configure_sqlite(dbapi_connection: Any, _connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        if ":memory:" not in database_url:
            cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


def init_engine(database_url: str | None = None) -> Engine:
    global engine, SessionLocal
    if engine is not None:
        engine.dispose()
    url = database_url or get_settings().database_url
    engine = create_engine(url, **_engine_options(url))
    _configure_sqlite(url, engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return engine


def get_engine() -> Engine:
    if engine is None:
        return init_engine()
    return engine


def get_session_factory() -> sessionmaker[Session]:
    if SessionLocal is None:
        init_engine()
    assert SessionLocal is not None
    return SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


init_engine()
