from tests.helpers import AUTH_PAYLOAD, register_user


def test_register_login_round_trip(client):
    created = register_user(client)
    assert created.status_code == 201
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["user"]["username"] == "frog_one"

    client.post("/api/v1/auth/logout")
    logged_out = client.get("/api/v1/auth/me")
    assert logged_out.status_code == 401
    assert logged_out.json()["detail"] == "请先登录"

    login = client.post(
        "/api/v1/auth/login",
        json={"username": AUTH_PAYLOAD["username"], "password": AUTH_PAYLOAD["password"]},
    )
    assert login.status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 200


def test_register_conflict(client):
    assert register_user(client).status_code == 201
    conflict = register_user(client)
    assert conflict.status_code == 409
    assert conflict.json()["detail"] == "用户名或邮箱已存在"


def test_login_wrong_password(client):
    register_user(client)
    client.post("/api/v1/auth/logout")
    response = client.post(
        "/api/v1/auth/login",
        json={"username": AUTH_PAYLOAD["username"], "password": "WrongPass123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "用户名或密码错误"


def test_me_requires_auth(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_desktop_login_hidden_without_desktop_mode(client):
    response = client.get("/api/v1/auth/desktop-login", follow_redirects=False)
    assert response.status_code == 404
