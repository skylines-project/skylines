from tests.data import add_fixtures, users


def test_read_user(db_session, client):
    john = users.john()
    add_fixtures(db_session, john)

    res = client.get('/users/{id}'.format(id=john.id))
    assert res.status_code == 200
    assert res.json == {
        u'id': john.id,
        u'firstName': u'John',
        u'lastName': u'Doe',
        u'name': u'John Doe',
        u'club': None,
        u'trackingCallsign': None,
        u'trackingDelay': 0,
        u'followers': 0,
        u'following': 0,
    }


def test_read_missing_user(client):
    res = client.get('/users/1000000000000')
    assert res.status_code == 404


def test_read_user_with_invalid_id(client):
    res = client.get('/users/abc')
    assert res.status_code == 404
