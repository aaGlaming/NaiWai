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
    assert limited.json()["detail"] == "留言过于频繁，请稍后再试"
