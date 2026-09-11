from app.config import default_sqlite_url


def test_default_database_is_sqlite():
    assert default_sqlite_url().startswith("sqlite:///")
    assert default_sqlite_url().endswith("data/naiwa.db")


def test_health_uses_sqlite(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"


def test_register_login_round_trip(client):
    payload = {
        "username": "frog_one",
        "password": "MilkFrog123!",
        "nickname": "奶蛙",
    }
    created = client.post("/api/v1/auth/register", json=payload)
    assert created.status_code == 201
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["user"]["username"] == "frog_one"

    client.post("/api/v1/auth/logout")
    logged_out = client.get("/api/v1/auth/me")
    assert logged_out.status_code == 401

    login = client.post("/api/v1/auth/login", json={"username": "frog_one", "password": "MilkFrog123!"})
    assert login.status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 200


def test_contact_rate_limit(client):
    form = {
        "name": "访客",
        "email": "guest@example.com",
        "subject": "你好",
        "message": "这是一条测试留言。",
    }
    for _ in range(5):
        assert client.post("/api/contact", json=form).status_code == 201
    limited = client.post("/api/contact", json=form)
    assert limited.status_code == 429
