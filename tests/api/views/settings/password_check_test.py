from tests.api import auth_for
from tests.data import add_fixtures, users


def test_correct_password(db_session, client):
    john = users.john()
    add_fixtures(db_session, john)

    res = client.post(
        "/settings/password/check",
        headers=auth_for(john),
        json={"password": john.original_password},
    )
    assert res.status_code == 200
    assert res.json == {"result": True}


def test_incorrect_password(db_session, client):
    john = users.john()
    add_fixtures(db_session, john)

    res = client.post(
        "/settings/password/check", headers=auth_for(john), json={"password": "foobar"}
    )
    assert res.status_code == 200
    assert res.json == {"result": False}


def test_invalid_json(db_session, client):
    john = users.john()
    add_fixtures(db_session, john)

    res = client.post(
        "/settings/password/check", headers=auth_for(john), data="foobar?"
    )
    assert res.status_code == 400


def test_unauthenticated(db_session, client):
    res = client.post("/settings/password/check")
    assert res.status_code == 401
