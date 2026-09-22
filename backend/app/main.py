import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError, app_error_handler
from app.core.logging import setup_logging
from app.database import get_engine
from app.paths import frontend_dist_dir, images_dir

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("NAIWA API starting")
    yield
    get_engine().dispose()
    logger.info("NAIWA API stopped")


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()
    application = FastAPI(
        title="奶蛙世界 API",
        description="奶蛙世界网站后端 API",
        version="2.0.0",
        lifespan=lifespan,
    )
    application.add_exception_handler(AppError, app_error_handler)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix="/api")

    image_assets = images_dir()
    if image_assets.exists():
        application.mount("/images", StaticFiles(directory=str(image_assets)), name="images")

    @application.get("/")
    def root():
        index = frontend_dist_dir() / "index.html"
        if index.exists():
            return FileResponse(index)
        return {"message": "🐸 奶蛙世界 API", "docs": "/docs", "health": "/api/health"}

    frontend_assets = frontend_dist_dir()
    if frontend_assets.exists():
        application.mount("/", StaticFiles(directory=str(frontend_assets), html=True), name="frontend")
    return application


app = create_app()
