from skylines.model import User
from tests.api import auth_for
from tests.data import add_fixtures, users


def test_generate(db_session, client):
    john = users.john()
    add_fixtures(db_session, john)

    old_key = john.tracking_key_hex

    res = client.post("/settings/tracking/key", headers=auth_for(john))
    assert res.status_code == 200

    new_key = res.json["key"]
    assert new_key != old_key
    assert User.get(john.id).tracking_key_hex == new_key


def test_unauthenticated(db_session, client):
    res = client.post("/settings/tracking/key")
    assert res.status_code == 401
