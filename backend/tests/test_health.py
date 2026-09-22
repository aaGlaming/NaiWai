from app.core.config import default_sqlite_url


def test_default_database_is_sqlite():
    assert default_sqlite_url().startswith("sqlite:///")
    assert default_sqlite_url().endswith("data/naiwa.db")


def test_health_uses_sqlite(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["desktop"] is False
