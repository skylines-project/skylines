from datetime import datetime

import pytest

from skylines.model import User, Club


@pytest.fixture(scope="function")
def fixtures(db_session):
    owner = User(first_name=u'John', last_name=u'Doe', password='jane123')
    db_session.add(owner)

    created_at = datetime(2016, 01, 15, 12, 34, 56)

    data = {
        'john': owner,
        'lva': Club(name=u'LV Aachen', website=u'http://www.lv-aachen.de', owner=owner, time_created=created_at),
        'sfn': Club(name=u'Sportflug Niederberg', time_created=created_at),
    }

    for v in data.itervalues():
        db_session.add(v)

    db_session.commit()
    return data


def test_lva(client, fixtures):
    id = fixtures['lva'].id

    res = client.get('/clubs/{}'.format(id))
    assert res.status_code == 200
    assert res.json == {
        u'id': id,
        u'name': u'LV Aachen',
        u'timeCreated': '2016-01-15T12:34:56+00:00',
        u'website': u'http://www.lv-aachen.de',
        u'isWritable': None,
        u'owner': {
            u'id': fixtures['john'].id,
            u'name': fixtures['john'].name,
        },
    }


def test_sfn(client, fixtures):
    id = fixtures['sfn'].id

    res = client.get('/clubs/{}'.format(id))
    assert res.status_code == 200
    assert res.json == {
        u'id': id,
        u'name': u'Sportflug Niederberg',
        u'timeCreated': '2016-01-15T12:34:56+00:00',
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
