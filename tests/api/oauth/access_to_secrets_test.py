import pytest

from immobilus import immobilus
from werkzeug.datastructures import Headers

from skylines.lib.basic_auth import encode as basic_auth_encode


def test_401_without_token(client):
    response = client.get("/secrets")
    assert response.status_code == 401
    assert response.json.get("error") == "invalid_token"


def test_401_with_invalid_authorization_header(client):
    headers = Headers()
    headers.set("Authorization", "Bearer")

    response = client.get("/secrets", headers=headers)
    assert response.status_code == 401
    assert response.json.get("error") == "invalid_token"


def test_401_with_unsupported_authorization_header(client):
    headers = Headers()
    headers.set("Authorization", "MAC 123456789")

    response = client.get("/secrets", headers=headers)
    assert response.status_code == 401
    assert response.json.get("error") == "invalid_token"


def test_401_with_invalid_token(client):
    headers = Headers()
    headers.set("Authorization", "Bearer invalid-token")

    response = client.get("/secrets", headers=headers)
    assert response.status_code == 401
    assert response.json.get("error") == "invalid_token"


def test_401_with_expired_token(client, access_token):
    headers = Headers()
    headers.set("Authorization", "Bearer " + access_token)

    with immobilus("2099-01-14"):
        response = client.get("/secrets", headers=headers)

    assert response.status_code == 401
    assert response.json.get("error") == "invalid_token"


def test_200_with_authorization_header(client, access_token):
    headers = Headers()
    headers.set("Authorization", "Bearer " + access_token)

    response = client.get("/secrets", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json.get("secrets"), list)


def test_401_with_invalid_token_parameter(client):
    response = client.get("/secrets?access_token=invalid-token")
    assert response.status_code == 401
    assert response.json.get("error") == "invalid_token"


def test_200_with_token_parameter(client, access_token):
    response = client.get("/secrets?access_token=" + access_token)
    assert response.status_code == 200
    assert isinstance(response.json.get("secrets"), list)


def test_401_with_invalid_credentials(client):
    headers = Headers()
    headers.set(
        "Authorization", basic_auth_encode("invalid-username", "invalid-password")
    )

    response = client.get("/secrets", headers=headers)
    assert response.status_code == 401
    assert response.json.get("error") == "invalid_token"


@pytest.mark.usefixtures("test_user")
def test_200_with_credentials(client):
    headers = Headers()
    headers.set("Authorization", basic_auth_encode("test@foo.com", "secret123"))

    response = client.get("/secrets", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json.get("secrets"), list)
