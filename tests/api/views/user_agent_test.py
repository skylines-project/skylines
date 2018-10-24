from werkzeug.datastructures import Headers


def test_request_with_user_agent_works(client):
    res = client.get("/")
    assert res.status_code == 404


def test_missing_user_agent_returns_403(client):
    headers = Headers()
    headers.set("User-Agent", "")

    res = client.get("/", headers=headers)
    assert res.status_code == 403

    json = res.json
    assert isinstance(json, dict)
    assert "User-Agent header" in json.get("message")
