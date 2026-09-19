from werkzeug.datastructures import Headers

ALLOWED_ORIGIN = "https://skylines.aero"
DISALLOWED_ORIGIN = "https://evil.example.com"


def test_no_cors(client):
    response = client.get("/")
    assert "Access-Control-Allow-Origin" not in response.headers
    assert "Access-Control-Allow-Credentials" not in response.headers
    assert "Access-Control-Allow-Methods" not in response.headers
    assert "Access-Control-Allow-Headers" not in response.headers


def test_cors_allowed_origin(client):
    headers = Headers()
    headers.set("Origin", ALLOWED_ORIGIN)

    response = client.get("/", headers=headers)
    assert response.headers.get("Access-Control-Allow-Origin") == ALLOWED_ORIGIN
    assert response.headers.get("Access-Control-Allow-Credentials") == "true"
    assert "Access-Control-Allow-Methods" not in response.headers
    assert "Access-Control-Allow-Headers" not in response.headers


def test_cors_disallowed_origin(client):
    headers = Headers()
    headers.set("Origin", DISALLOWED_ORIGIN)

    response = client.get("/", headers=headers)
    assert "Access-Control-Allow-Origin" not in response.headers
    assert "Access-Control-Allow-Credentials" not in response.headers


def test_cors_with_headers(client):
    headers = Headers()
    headers.set("Origin", ALLOWED_ORIGIN)
    headers.set("Access-Control-Request-Headers", "Authorization")

    response = client.get("/", headers=headers)
    assert response.headers.get("Access-Control-Allow-Origin") == ALLOWED_ORIGIN
    assert response.headers.get("Access-Control-Allow-Credentials") == "true"
    assert "Access-Control-Allow-Methods" not in response.headers
    assert response.headers.get("Access-Control-Allow-Headers") == "Authorization"


def test_cors_with_methods(client):
    headers = Headers()
    headers.set("Origin", ALLOWED_ORIGIN)
    headers.set("Access-Control-Request-Methods", "get, post")

    response = client.get("/", headers=headers)
    assert response.headers.get("Access-Control-Allow-Origin") == ALLOWED_ORIGIN
    assert response.headers.get("Access-Control-Allow-Credentials") == "true"
    assert response.headers.get("Access-Control-Allow-Methods") == "get, post"
    assert "Access-Control-Allow-Headers" not in response.headers


def test_cors_env_override(app, monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://custom.example.com,https://other.example.com")
    custom_origin = "https://custom.example.com"

    with app.test_client() as client:
        headers = Headers()
        headers.set("Origin", custom_origin)
        headers.set("User-Agent", "py.test")

        response = client.get("/", headers=headers)
        assert response.headers.get("Access-Control-Allow-Origin") == custom_origin
        assert response.headers.get("Access-Control-Allow-Credentials") == "true"


def test_cors_env_override_blocks_default(app, monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://custom.example.com")

    with app.test_client() as client:
        headers = Headers()
        headers.set("Origin", ALLOWED_ORIGIN)
        headers.set("User-Agent", "py.test")

        response = client.get("/", headers=headers)
        assert "Access-Control-Allow-Origin" not in response.headers


def test_cors_localhost_allowed_in_debug(app):
    """Localhost origins are allowed when DEBUG=True (testing config inherits DEBUG from default)."""
    assert app.config.get("DEBUG") is True

    with app.test_client() as client:
        headers = Headers()
        headers.set("Origin", "http://localhost:5000")
        headers.set("User-Agent", "py.test")

        response = client.get("/", headers=headers)
        assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:5000"
        assert response.headers.get("Access-Control-Allow-Credentials") == "true"
