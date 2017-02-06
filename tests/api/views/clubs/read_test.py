from skylines.model import User
from tests.data import clubs


def test_lva(db_session, client):
    john = User(first_name=u'John', last_name=u'Doe', password='jane123')

    lva = clubs.lva()
    lva.owner = john

    db_session.add(lva)
    db_session.commit()

    res = client.get('/clubs/{id}'.format(id=lva.id))
    assert res.status_code == 200
    assert res.json == {
        'id': lva.id,
        'name': 'LV Aachen',
        'timeCreated': '2015-12-24T12:34:56+00:00',
        'website': 'http://www.lv-aachen.de',
        'isWritable': None,
        'owner': {
            'id': john.id,
            'name': john.name,
        },
    }


def test_sfn(db_session, client):
    sfn = clubs.sfn()

    db_session.add(sfn)
    db_session.commit()

    res = client.get('/clubs/{id}'.format(id=sfn.id))
    assert res.status_code == 200
    assert res.json == {
        u'id': sfn.id,
        u'name': u'Sportflug Niederberg',
        u'timeCreated': '2017-01-01T12:34:56+00:00',
        u'website': None,
        u'isWritable': None,
        u'owner': None,
    }


def test_missing(client):
    res = client.get('/clubs/10000000')
    assert res.status_code == 404


def test_invalid_id(client):
    res = client.get('/clubs/abc')
    assert res.status_code == 404
