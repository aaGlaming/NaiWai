import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-naiwa"
os.environ["COOKIE_SECURE"] = "false"
os.environ["DESKTOP_MODE"] = "false"

from collections.abc import Generator

import pytest
from app.core.config import get_settings
from fastapi.testclient import TestClient

get_settings.cache_clear()

from app.database import Base, get_db, get_session_factory, init_engine
from app.main import app
from app.services.contact import contact_limiter


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    contact_limiter.reset()
    engine = init_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = get_session_factory()()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
