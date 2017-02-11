from tests.data import add_fixtures, users


def test_list_users(db_session, client):
    john = users.john()
    add_fixtures(db_session, john)

    res = client.get('/users/')
    assert res.status_code == 200
    assert res.json == {
        u'users': [{
            u'id': john.id,
            u'name': u'John Doe',
            u'club': None,
        }]
    }
