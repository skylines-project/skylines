from tests.data import add_fixtures, users, clubs


def test_list_users(db_session, client):
    john = users.john()
    add_fixtures(db_session, john)

    res = client.get("/users/")
    assert res.status_code == 200
    assert res.json == {
        u"users": [{u"id": john.id, u"name": u"John Doe", u"club": None}]
    }


def test_with_club(db_session, client):
    john = users.john(club=clubs.lva())
    add_fixtures(db_session, john)

    res = client.get("/users")
    assert res.status_code == 200
    assert res.json == {
        u"users": [
            {
                u"id": john.id,
                u"name": u"John Doe",
                u"club": {u"id": john.club.id, u"name": u"LV Aachen"},
            }
        ]
    }


def test_with_club_parameter(db_session, client):
    john = users.john(club=clubs.lva())
    add_fixtures(db_session, john, users.jane(), users.max())

    res = client.get("/users")
    assert res.status_code == 200
    assert len(res.json["users"]) == 3

    res = client.get("/users?club={club}".format(club=john.club.id))
    assert res.status_code == 200
    assert len(res.json["users"]) == 1
    assert res.json == {u"users": [{u"id": john.id, u"name": u"John Doe"}]}
