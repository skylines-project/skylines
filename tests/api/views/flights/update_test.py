import base64

import pytest

from flask import json

from skylines.model import User, Club, Flight, IGCFile
from werkzeug.datastructures import Headers
from tests.data import add_fixtures, igcs, flights


@pytest.fixture
def club_1():
    return Club(name=u'LV Aachen')


@pytest.fixture
def club_2():
    return Club(name=u'Sportflug Niederberg')


@pytest.fixture
def user_with_club(club_1):
    return User(first_name=u'John', last_name=u'Smith',
                email_address='john@smith.com', password='123456', club=club_1)


@pytest.fixture
def user_with_same_club(club_1):
    return User(first_name=u'Fred', last_name=u'Bloggs',
                email_address='fred@bloggs.com', password='123456', club=club_1)


@pytest.fixture
def user_with_other_club(club_2):
    return User(first_name=u'Joe', last_name=u'Bloggs',
                email_address='joe@bloggs.com', password='123456', club=club_2)


@pytest.fixture
def user_without_club():
    return User(first_name=u'Club', last_name=u'Less',
                email_address='club@less.com', password='123456')


@pytest.fixture
def user_without_club_2():
    return User(first_name=u'No', last_name=u'Club',
                email_address='no@club.com', password='123456')


def auth_for(user):
    password = '123456'

    headers = Headers()
    headers.add('Authorization', 'Basic ' + base64.b64encode(user.email_address + ':' + password))

    return headers


def test_pilot_changing_correct_with_co(db_session, client, user_with_club, user_with_same_club):
    """ Pilot is changing copilot to user from same club. """

    flight = flights.one(pilot=user_with_club, igc_file=igcs.simple(owner=user_with_club))
    add_fixtures(db_session, flight, user_with_club, user_with_same_club)

    response = client.post('/flights/{id}'.format(id=flight.id), headers=auth_for(user_with_club), json={
        'pilotId': user_with_club.id,
        'copilotId': user_with_same_club.id,
    })

    assert response.status_code == 200


def test_pilot_changing_disowned_flight(db_session, client,
                                        user_with_club, user_with_same_club, user_with_other_club):
    """ Unrelated user is trying to change pilots. """

    flight = flights.one(pilot=user_with_club, igc_file=igcs.simple(owner=user_with_club))
    add_fixtures(db_session, flight, user_with_club, user_with_same_club, user_with_other_club)

    response = client.post('/flights/{id}'.format(id=flight.id), headers=auth_for(user_with_same_club), json={
        'pilotId': user_with_club.id,
        'copilotId': user_with_other_club.id,
    })

    assert response.status_code == 403


def test_pilot_changing_disallowed_pilot(db_session, client, user_with_club, user_with_other_club):
    """ Pilot is trying to change pilot to user from different club. """

    flight = flights.one(pilot=user_with_club, igc_file=igcs.simple(owner=user_with_club))
    add_fixtures(db_session, flight, user_with_club, user_with_other_club)

    response = client.post('/flights/{id}'.format(id=flight.id), headers=auth_for(user_with_club), json={
        'pilotId': user_with_other_club.id,
        'copilotId': user_with_club.id,
    })

    assert response.status_code == 422


def test_pilot_changing_disallowed_copilot(db_session, client, user_with_club, user_with_other_club):
    """ Pilot is trying to change copilot to user from different club. """

    flight = flights.one(pilot=user_with_club, igc_file=igcs.simple(owner=user_with_club))
    add_fixtures(db_session, flight, user_with_club, user_with_other_club)

    response = client.post('/flights/{id}'.format(id=flight.id), headers=auth_for(user_with_club), json={
        'pilotId': user_with_club.id,
        'copilotId': user_with_other_club.id,
    })

    assert response.status_code == 422


def test_pilot_changing_same_pilot_and_co(db_session, client, user_with_club):
    """ Pilot is trying to change copilot to the same as pilot. """

    flight = flights.one(pilot=user_with_club, igc_file=igcs.simple(owner=user_with_club))
    add_fixtures(db_session, flight, user_with_club)

    response = client.post('/flights/{id}'.format(id=flight.id), headers=auth_for(user_with_club), json={
        'pilotId': user_with_club.id,
        'copilotId': user_with_club.id,
    })

    assert response.status_code == 422


def test_pilot_changing_pilot_and_co_null(db_session, client, user_with_club):
    """ Pilot is changing pilot and copilot to unknown user accounts. """

    flight = flights.one(pilot=user_with_club, igc_file=igcs.simple(owner=user_with_club))
    add_fixtures(db_session, flight, user_with_club)

    response = client.post('/flights/{id}'.format(id=flight.id), headers=auth_for(user_with_club), json={
        'pilotName': 'foo',
        'copilotName': 'bar',
    })

    assert response.status_code == 200


def test_pilot_changing_clubless_co(db_session, client, user_with_club, user_without_club):
    """ Pilot is trying to change copilot to user without club. """

    flight = flights.one(pilot=user_with_club, igc_file=igcs.simple(owner=user_with_club))
    add_fixtures(db_session, flight, user_with_club, user_without_club)

    response = client.post('/flights/{id}'.format(id=flight.id), headers=auth_for(user_with_club), json={
        'pilotId': user_with_club.id,
        'copilotId': user_without_club.id,
    })

    assert response.status_code == 422


def test_pilot_changing_clubless_pilot_and_co(db_session, client, user_without_club, user_without_club_2):
    """ Pilot without club is trying to change copilot to user without club. """

    flight = flights.one(pilot=user_without_club, igc_file=igcs.simple(owner=user_without_club))
    add_fixtures(db_session, flight, user_without_club, user_without_club_2)

    response = client.post('/flights/{id}'.format(id=flight.id), headers=auth_for(user_without_club), json={
        'pilotId': user_without_club.id,
        'copilotId': user_without_club_2.id,
    })

    assert response.status_code == 422
