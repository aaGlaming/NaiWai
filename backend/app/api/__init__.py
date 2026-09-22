from fastapi import APIRouter

from app.api import auth, contact, health, images, users

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(images.router, tags=["images"])
api_router.include_router(contact.router, tags=["contact"])
api_router.include_router(auth.router, prefix="/v1", tags=["auth"])
api_router.include_router(users.router, prefix="/v1", tags=["users"])
