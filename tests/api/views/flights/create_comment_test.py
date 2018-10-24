from tests.api import auth_for
from tests.data import add_fixtures, igcs, flights, users, flight_comments


def test_create(db_session, client):
    john = users.john()
    flight = flights.one(igc_file=igcs.simple(owner=john))
    comment = flight_comments.yeah(flight=flight)
    add_fixtures(db_session, flight, comment, john)

    res = client.get("/flights/{id}?extended".format(id=flight.id))
    assert res.status_code == 200
    assert res.json["comments"] == [{u"user": None, u"text": u"Yeah!"}]

    res = client.post(
        "/flights/{id}/comments".format(id=flight.id),
        headers=auth_for(john),
        json={u"text": u"foobar"},
    )
    assert res.status_code == 200
    assert res.json == {}

    res = client.get("/flights/{id}?extended".format(id=flight.id))
    assert res.status_code == 200
    assert res.json["comments"] == [
        {u"user": None, u"text": u"Yeah!"},
        {u"user": {u"id": john.id, u"name": u"John Doe"}, u"text": u"foobar"},
    ]


def test_unauthenticated(db_session, client):
    flight = flights.one(igc_file=igcs.simple(owner=users.john()))
    comment = flight_comments.yeah(flight=flight)
    add_fixtures(db_session, flight, comment)

    res = client.get("/flights/{id}?extended".format(id=flight.id))
    assert res.status_code == 200
    assert res.json["comments"] == [{u"user": None, u"text": u"Yeah!"}]

    res = client.post(
        "/flights/{id}/comments".format(id=flight.id), json={u"text": u"foobar"}
    )
    assert res.status_code == 401
    assert res.json == {
        u"error": u"invalid_token",
        u"message": u"Bearer token not found.",
    }

    res = client.get("/flights/{id}?extended".format(id=flight.id))
    assert res.status_code == 200
    assert res.json["comments"] == [{u"user": None, u"text": u"Yeah!"}]


def test_missing_flight(db_session, client):
    john = users.john()
    add_fixtures(db_session, john)

    res = client.post(
        "/flights/{id}/comments".format(id=1000000),
        headers=auth_for(john),
        json={u"text": u"foobar"},
    )
    assert res.status_code == 404
    assert res.json == {
        u"message": u"Sorry, there is no such record (1000000) in our database."
    }


def test_validation_error(db_session, client):
    john = users.john()
    flight = flights.one(igc_file=igcs.simple(owner=john))
    add_fixtures(db_session, flight, john)

    res = client.post(
        "/flights/{id}/comments".format(id=flight.id), headers=auth_for(john), json={}
    )
    assert res.status_code == 422
    assert res.json == {
        u"error": u"validation-failed",
        u"fields": {u"text": [u"Missing data for required field."]},
    }


def test_invalid_data(db_session, client):
    john = users.john()
    flight = flights.one(igc_file=igcs.simple(owner=john))
    add_fixtures(db_session, flight, john)

    res = client.post(
        "/flights/{id}/comments".format(id=flight.id),
        headers=auth_for(john),
        data="foobar?",
    )
    assert res.status_code == 400
    assert res.json == {u"error": u"invalid-request"}
