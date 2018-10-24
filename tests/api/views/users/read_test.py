from skylines.model import Follower
from tests.api import auth_for
from tests.data import add_fixtures, users


def test_read_user(db_session, client):
    john = users.john()
    add_fixtures(db_session, john)

    res = client.get("/users/{id}".format(id=john.id))
    assert res.status_code == 200
    assert res.json == {
        u"id": john.id,
        u"firstName": u"John",
        u"lastName": u"Doe",
        u"name": u"John Doe",
        u"club": None,
        u"trackingCallsign": None,
        u"trackingDelay": 0,
        u"followers": 0,
        u"following": 0,
    }


def test_following(db_session, client):
    john = users.john()
    jane = users.jane()
    add_fixtures(db_session, john, jane)
    Follower.follow(john, jane)

    res = client.get("/users/{id}".format(id=john.id))
    assert res.status_code == 200
    assert res.json["following"] == 1

    res = client.get("/users/{id}".format(id=jane.id))
    assert res.status_code == 200
    assert res.json["followers"] == 1
    assert "followed" not in res.json

    res = client.get("/users/{id}".format(id=jane.id), headers=auth_for(john))
    assert res.status_code == 200
    assert res.json["followers"] == 1
    assert res.json["followed"] == True


def test_read_missing_user(client):
    res = client.get("/users/1000000000000")
    assert res.status_code == 404


def test_read_user_with_invalid_id(client):
    res = client.get("/users/abc")
    assert res.status_code == 404
