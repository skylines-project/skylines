from skylines.model import Club
from tests.api import auth_for
from tests.data import add_fixtures, clubs


def test_update(db_session, client, test_user):
    sfn = clubs.sfn()
    test_user.club = sfn
    add_fixtures(db_session, sfn)

    res = client.post('/clubs/{id}'.format(id=sfn.id), headers=auth_for(test_user), json={
        'name': 'foobar',
        'website': 'https://foobar.de',
    })
    assert res.status_code == 200

    club = Club.get(sfn.id)
    assert club.name == 'foobar'
    assert club.website == 'https://foobar.de'


def test_update_without_permission(db_session, client, test_user):
    sfn = clubs.sfn()
    add_fixtures(db_session, sfn)

    res = client.post('/clubs/{id}'.format(id=sfn.id), headers=auth_for(test_user), json={
        'name': 'foobar',
        'website': 'https://foobar.de',
    })
    assert res.status_code == 403

    club = Club.get(sfn.id)
    assert club.name == 'Sportflug Niederberg'
    assert club.website == None


def test_update_without_authentication(db_session, client):
    sfn = clubs.sfn()
    add_fixtures(db_session, sfn)

    res = client.post('/clubs/{id}'.format(id=sfn.id), json={
        'name': 'foobar',
        'website': 'https://foobar.de',
    })
    assert res.status_code == 401

    club = Club.get(sfn.id)
    assert club.name == 'Sportflug Niederberg'
    assert club.website == None


def test_missing(db_session, client, test_user):
    res = client.post('/clubs/1000000000', headers=auth_for(test_user), json={
        'name': 'foobar',
        'website': 'https://foobar.de',
    })
    assert res.status_code == 404


def test_invalid_id(db_session, client, test_user):
    res = client.post('/clubs/abc', headers=auth_for(test_user), json={
        'name': 'foobar',
        'website': 'https://foobar.de',
    })
    assert res.status_code == 404
