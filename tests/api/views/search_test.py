# coding=utf-8

import pytest
from flask import Response, json
from flask.testing import FlaskClient

from skylines.model import User, Club, Airport


@pytest.fixture(autouse=True)
def fixtures(db_session):
    data = {
        'john': User(first_name=u'John', last_name=u'Doe', password='jane123'),
        'jane': User(first_name=u'Jane', last_name=u'Doe', password='johnny'),
        'lva': Club(name=u'LV Aachen', website='https://www.lv-aachen.de'),
        'sfn': Club(name=u'Sportflug Niederberg'),
        'edka': Airport(name=u'Aachen-Merzbrück', country_code='DE', icao='EDKA', frequency='122.875'),
        'mbg': Airport(name=u'Meiersberg', country_code='DE'),
    }

    for v in data.itervalues():
        db_session.add(v)

    db_session.commit()
    return data


def test_search(client, default_headers, fixtures):
    assert isinstance(client, FlaskClient)

    edka = {
        'type': 'airport',
        'id': fixtures['edka'].id,
        'name': u'Aachen-Merzbrück',
        'icao': 'EDKA',
        'frequency': '122.875',
    }
    lva = {
        'type': 'club',
        'id': fixtures['lva'].id,
        'name': u'LV Aachen',
        'website': 'https://www.lv-aachen.de',
    }

    response = client.get('/search?text=aachen', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200

    data = json.loads(response.data)['results']
    assert len(data) == 2
    assert edka in data
    assert lva in data


def test_search2(client, default_headers, fixtures):
    assert isinstance(client, FlaskClient)

    jane = {
        'type': 'user',
        'id': fixtures['jane'].id,
        'name': u'Jane Doe',
    }
    john = {
        'type': 'user',
        'id': fixtures['john'].id,
        'name': u'John Doe',
    }

    response = client.get('/search?text=doe', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200

    data = json.loads(response.data)['results']
    assert len(data) == 2
    assert jane in data
    assert john in data


def test_missing_search_text(client, default_headers):
    assert isinstance(client, FlaskClient)

    response = client.get('/search', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200

    data = json.loads(response.data)['results']
    assert len(data) == 0
