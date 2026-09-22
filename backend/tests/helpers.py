from app.database import get_session_factory
from app.models import Image
from fastapi.testclient import TestClient

AUTH_PAYLOAD = {
    "username": "frog_one",
    "password": "MilkFrog123!",
    "nickname": "奶蛙",
}


def register_user(client: TestClient, **overrides):
    payload = {**AUTH_PAYLOAD, **overrides}
    return client.post("/api/v1/auth/register", json=payload)


def add_image(filename: str = "frog.png", category: str = "emoji") -> Image:
    db = get_session_factory()()
    image = Image(filename=filename, category=category, extension="png", rarity="N")
    db.add(image)
    db.commit()
    db.refresh(image)
    db.close()
    return image
