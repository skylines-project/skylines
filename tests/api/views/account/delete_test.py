from tests.api import auth_for


def test_delete_account(client, test_user):
    res = client.get("/users/{id}".format(id=test_user.id))
    assert res.status_code == 200

    res = client.delete(
        "/account",
        headers=auth_for(test_user),
        json={"password": test_user.original_password},
    )
    assert res.status_code == 200
    assert res.json == {}

    res = client.get("/users/{id}".format(id=test_user.id))
    assert res.status_code == 404


def test_delete_account_with_wrong_password(client, test_user):
    res = client.delete(
        "/account", headers=auth_for(test_user), json={"password": "wrong-password"}
    )
    assert res.status_code == 403


def test_delete_account_with_missing_password(client, test_user):
    res = client.delete("/account", headers=auth_for(test_user))
    assert res.status_code == 400


def test_delete_account_without_authentication(client):
    res = client.delete("/account")
    assert res.status_code == 401


def test_delete_account_invalidates_auth_tokens(client, test_user):
    res = client.get("/settings".format(id=test_user.id), headers=auth_for(test_user))
    assert res.status_code == 200

    res = client.delete(
        "/account",
        headers=auth_for(test_user),
        json={"password": test_user.original_password},
    )
    assert res.status_code == 200
    assert res.json == {}

    res = client.get("/settings".format(id=test_user.id), headers=auth_for(test_user))
    assert res.status_code == 401
