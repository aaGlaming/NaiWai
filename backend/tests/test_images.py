from tests.helpers import add_image


def test_image_list_and_detail(client):
    add_image("frog.png")
    listed = client.get("/api/images")
    assert listed.status_code == 200
    body = listed.json()
    assert body["total"] == 1
    assert body["images"][0]["filename"] == "frog.png"
    assert body["images"][0]["url"] == "/images/frog.png"

    detail = client.get("/api/images/frog.png")
    assert detail.status_code == 200
    assert detail.json()["filename"] == "frog.png"


def test_image_not_found(client):
    response = client.get("/api/images/missing.png")
    assert response.status_code == 404
    assert response.json()["detail"] == "图片不存在"


def test_image_search_escapes_like_wildcards(client):
    add_image("100_percent.png")
    add_image("other.png")
    response = client.get("/api/images", params={"q": "100_percent"})
    assert response.status_code == 200
    filenames = [item["filename"] for item in response.json()["images"]]
    assert filenames == ["100_percent.png"]
