from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import auth, contact, images, users
from app.config import get_settings
from app.database import engine
from app.paths import frontend_dist_dir, images_dir

settings = get_settings()
app = FastAPI(title="奶蛙世界 API", description="奶蛙世界网站后端 API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(images.router, prefix="/api", tags=["images"])
app.include_router(contact.router, prefix="/api", tags=["contact"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])

image_assets = images_dir()
if image_assets.exists():
    app.mount("/images", StaticFiles(directory=str(image_assets)), name="images")


@app.get("/")
def root():
    index = frontend_dist_dir() / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "🐸 奶蛙世界 API", "docs": "/docs", "health": "/api/health"}


@app.get("/api/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        database = "ok"
    except Exception:
        database = "unavailable"
    return {"status": "ok", "database": database, "desktop": settings.desktop_mode,
            "message": "奶蛙世界 API 运行中 🐸"}


frontend_assets = frontend_dist_dir()
if frontend_assets.exists():
    app.mount("/", StaticFiles(directory=str(frontend_assets), html=True), name="frontend")
