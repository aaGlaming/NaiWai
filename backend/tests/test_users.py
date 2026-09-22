from tests.helpers import add_image, register_user


def test_favorites_collection_and_events(client):
    register_user(client)
    add_image("frog.png")

    added = client.put("/api/v1/me/favorites/frog.png")
    assert added.status_code == 200
    data = client.get("/api/v1/me/data")
    assert data.json()["favorites"] == ["frog.png"]

    collected = client.put("/api/v1/me/collection/frog.png")
    assert collected.status_code == 200
    data = client.get("/api/v1/me/data")
    assert data.json()["collection"] == ["frog.png"]

    event = client.post("/api/v1/me/events", json={"event": "draw", "count": 2, "ssr": 1, "pity": 0})
    assert event.status_code == 200
    stats = event.json()["data"]["stats"]
    assert stats["draws"] == 2
    assert stats["ssrCount"] == 1

    mine = client.post("/api/v1/me/events", json={"event": "mine"})
    assert mine.status_code == 200
    assert mine.json()["data"]["stats"]["mines"] == 1

    daily = client.post("/api/v1/me/events", json={"event": "daily_mine"})
    assert daily.status_code == 200
    assert daily.json()["data"]["stats"]["lastDailyMine"]

    removed = client.delete("/api/v1/me/favorites/frog.png")
    assert removed.status_code == 200
    assert client.get("/api/v1/me/data").json()["favorites"] == []


def test_unknown_event(client):
    register_user(client)
    response = client.post("/api/v1/me/events", json={"event": "not-a-real-event"})
    assert response.status_code == 400
    assert response.json()["detail"] == "不支持的统计事件"


def test_favorite_missing_image(client):
    register_user(client)
    response = client.put("/api/v1/me/favorites/missing.png")
    assert response.status_code == 404


def test_import_local_data_once(client):
    register_user(client)
    add_image("frog.png")
    payload = {
        "favorites": ["frog.png"],
        "collection": ["frog.png"],
        "unlocked": [],
        "stats": {"draws": 3, "ssrCount": 1},
    }
    first = client.post("/api/v1/me/import-local-data", json=payload)
    assert first.status_code == 200
    assert first.json()["data"]["favorites"] == ["frog.png"]
    assert first.json()["data"]["stats"]["draws"] == 3

    second = client.post("/api/v1/me/import-local-data", json=payload)
    assert second.status_code == 409
    assert second.json()["detail"] == "本地数据已经导入过"


def test_me_data_requires_auth(client):
    response = client.get("/api/v1/me/data")
    assert response.status_code == 401
