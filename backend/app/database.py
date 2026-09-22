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


def ensure_sqlite_columns() -> None:
    eng = get_engine()
    if eng.dialect.name != "sqlite":
        return
    with eng.begin() as connection:
        tables = {
            row[0] for row in connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'").all()
        }
        if "user_stats" not in tables:
            return
        columns = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(user_stats)").all()}
        if "mines" not in columns:
            connection.exec_driver_sql("ALTER TABLE user_stats ADD COLUMN mines INTEGER NOT NULL DEFAULT 0")
        if "last_daily_mine" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE user_stats ADD COLUMN last_daily_mine VARCHAR(10) NOT NULL DEFAULT ''"
            )


init_engine()
