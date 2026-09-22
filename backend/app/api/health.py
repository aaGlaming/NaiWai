import logging

from fastapi import APIRouter

from app.core.config import get_settings
from app.database import get_engine
from app.schemas.common import HealthOut

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthOut)
def health_check() -> HealthOut:
    settings = get_settings()
    try:
        with get_engine().connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        database = "ok"
    except Exception:
        logger.exception("health check database probe failed")
        database = "unavailable"
    return HealthOut(
        status="ok",
        database=database,
        desktop=settings.desktop_mode,
        message="奶蛙世界 API 运行中 🐸",
    )
