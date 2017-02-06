from skylines.model import Club
from tests.api import basic_auth
from tests.data import add_fixtures, clubs


def test_create(db_session, client, test_user):
    headers = basic_auth(test_user.email_address, test_user.original_password)

    res = client.put('/clubs', headers=headers, json={
        'name': 'LV Aachen',
    })
    assert res.status_code == 200

    club = Club.get(res.json['id'])
    assert club
    assert club.owner_id == test_user.id


def test_without_authentication(db_session, client):
    res = client.put('/clubs', json={
        'name': 'LV Aachen',
    })
    assert res.status_code == 401
    assert res.json['error'] == 'invalid_token'


def test_non_json_data(db_session, client, test_user):
    headers = basic_auth(test_user.email_address, test_user.original_password)

    res = client.put('/clubs', headers=headers, data='foobar?')
    assert res.status_code == 400
    assert res.json['error'] == 'invalid-request'


def test_invalid_data(db_session, client, test_user):
    headers = basic_auth(test_user.email_address, test_user.original_password)

    res = client.put('/clubs', headers=headers, json={
        'name': '',
    })
    assert res.status_code == 422
    assert res.json['error'] == 'validation-failed'


def test_existing_club(db_session, client, test_user):
    lva = clubs.lva()
    add_fixtures(db_session, lva)

    headers = basic_auth(test_user.email_address, test_user.original_password)

    res = client.put('/clubs', headers=headers, json={
        'name': 'LV Aachen',
    })
    assert res.status_code == 422
    assert res.json['error'] == 'duplicate-club-name'
