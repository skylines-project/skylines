from datetime import datetime

import pytest
from flask import Response, json
from flask.testing import FlaskClient

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


def test_lva(client, default_headers, fixtures):
    assert isinstance(client, FlaskClient)

    id = fixtures['lva'].id

    response = client.get('/clubs/{}'.format(id), headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {
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


def test_sfn(client, default_headers, fixtures):
    assert isinstance(client, FlaskClient)

    id = fixtures['sfn'].id

    response = client.get('/clubs/{}'.format(id), headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {
        u'id': id,
        u'name': u'Sportflug Niederberg',
        u'timeCreated': '2016-01-15T12:34:56+00:00',
        u'website': None,
        u'isWritable': None,
        u'owner': None,
    }


def test_missing(client, default_headers):
    assert isinstance(client, FlaskClient)

    response = client.get('/clubs/10000000', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 404


def test_invalid_id(client, default_headers):
    assert isinstance(client, FlaskClient)

    response = client.get('/clubs/abc', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 404
