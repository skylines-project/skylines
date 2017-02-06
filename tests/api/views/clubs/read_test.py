from tests.api import basic_auth
from tests.data import add_fixtures, clubs, users


def test_lva(db_session, client):
    lva = clubs.lva()
    lva.owner = users.john()
    add_fixtures(db_session, lva)

    res = client.get('/clubs/{id}'.format(id=lva.id))
    assert res.status_code == 200
    assert res.json == {
        'id': lva.id,
        'name': 'LV Aachen',
        'timeCreated': '2015-12-24T12:34:56+00:00',
        'website': 'http://www.lv-aachen.de',
        'isWritable': False,
        'owner': {
            'id': lva.owner.id,
            'name': lva.owner.name,
        },
    }


def test_sfn(db_session, client):
    sfn = clubs.sfn()
    add_fixtures(db_session, sfn)

    res = client.get('/clubs/{id}'.format(id=sfn.id))
    assert res.status_code == 200
    assert res.json == {
        u'id': sfn.id,
        u'name': u'Sportflug Niederberg',
        u'timeCreated': '2017-01-01T12:34:56+00:00',
        u'website': None,
        u'isWritable': False,
        u'owner': None,
    }


def test_writable(db_session, client):
    lva = clubs.lva()
    john = users.john()
    john.club = lva
    add_fixtures(db_session, lva, john)

    headers = basic_auth(john.email_address, john.original_password)

    res = client.get('/clubs/{id}'.format(id=lva.id), headers=headers)
    assert res.status_code == 200
    assert res.json == {
        'id': lva.id,
        'name': 'LV Aachen',
        'timeCreated': '2015-12-24T12:34:56+00:00',
        'website': 'http://www.lv-aachen.de',
        'isWritable': True,
        'owner': None,
    }


def test_missing(client):
    res = client.get('/clubs/10000000')
    assert res.status_code == 404


def test_invalid_id(client):
    res = client.get('/clubs/abc')
    assert res.status_code == 404
