from tests.api import auth_for
from tests.data import add_fixtures, igcs, flights, clubs, users


def test_pilot_changing_correct_with_co(db_session, client):
    """ Pilot is changing copilot to user from same club. """

    john = users.john(club=clubs.lva())
    jane = users.jane(club=john.club)
    flight = flights.one(igc_file=igcs.simple(owner=john))
    add_fixtures(db_session, flight, john, jane)

    response = client.post(
        "/flights/{id}".format(id=flight.id),
        headers=auth_for(john),
        json={"pilotId": john.id, "copilotId": jane.id},
    )

    assert response.status_code == 200


def test_pilot_changing_disowned_flight(db_session, client):
    """ Unrelated user is trying to change pilots. """

    john = users.john(club=clubs.lva())
    jane = users.jane(club=john.club)
    max = users.max(club=clubs.sfn())
    flight = flights.one(igc_file=igcs.simple(owner=john))
    add_fixtures(db_session, flight, john, jane, max)

    response = client.post(
        "/flights/{id}".format(id=flight.id),
        headers=auth_for(jane),
        json={"pilotId": john.id, "copilotId": max.id},
    )

    assert response.status_code == 403


def test_pilot_changing_disallowed_pilot(db_session, client):
    """ Pilot is trying to change pilot to user from different club. """

    john = users.john(club=clubs.lva())
    max = users.max(club=clubs.sfn())
    flight = flights.one(igc_file=igcs.simple(owner=john))
    add_fixtures(db_session, flight, john, max)

    response = client.post(
        "/flights/{id}".format(id=flight.id),
        headers=auth_for(john),
        json={"pilotId": max.id, "copilotId": john.id},
    )

    assert response.status_code == 422


def test_pilot_changing_disallowed_copilot(db_session, client):
    """ Pilot is trying to change copilot to user from different club. """

    john = users.john(club=clubs.lva())
    max = users.max(club=clubs.sfn())
    flight = flights.one(igc_file=igcs.simple(owner=john))
    add_fixtures(db_session, flight, john, max)

    response = client.post(
        "/flights/{id}".format(id=flight.id),
        headers=auth_for(john),
        json={"pilotId": john.id, "copilotId": max.id},
    )

    assert response.status_code == 422


def test_pilot_changing_same_pilot_and_co(db_session, client):
    """ Pilot is trying to change copilot to the same as pilot. """

    john = users.john(club=clubs.lva())
    flight = flights.one(igc_file=igcs.simple(owner=john))
    add_fixtures(db_session, flight, john)

    response = client.post(
        "/flights/{id}".format(id=flight.id),
        headers=auth_for(john),
        json={"pilotId": john.id, "copilotId": john.id},
    )

    assert response.status_code == 422


def test_pilot_changing_pilot_and_co_null(db_session, client):
    """ Pilot is changing pilot and copilot to unknown user accounts. """

    john = users.john(club=clubs.lva())
    flight = flights.one(igc_file=igcs.simple(owner=john))
    add_fixtures(db_session, flight, john)

    response = client.post(
        "/flights/{id}".format(id=flight.id),
        headers=auth_for(john),
        json={"pilotName": "foo", "copilotName": "bar"},
    )

    assert response.status_code == 200


def test_pilot_changing_clubless_co(db_session, client):
    """ Pilot is trying to change copilot to user without club. """

    john = users.john(club=clubs.lva())
    jane = users.jane()
    flight = flights.one(igc_file=igcs.simple(owner=john))
    add_fixtures(db_session, flight, john, jane)

    response = client.post(
        "/flights/{id}".format(id=flight.id),
        headers=auth_for(john),
        json={"pilotId": john.id, "copilotId": jane.id},
    )

    assert response.status_code == 422


def test_pilot_changing_clubless_pilot_and_co(db_session, client):
    """ Pilot without club is trying to change copilot to user without club. """

    john = users.john()
    jane = users.jane()
    flight = flights.one(igc_file=igcs.simple(owner=john))
    add_fixtures(db_session, flight, john, jane)

    response = client.post(
        "/flights/{id}".format(id=flight.id),
        headers=auth_for(john),
        json={"pilotId": john.id, "copilotId": jane.id},
    )

    assert response.status_code == 422
