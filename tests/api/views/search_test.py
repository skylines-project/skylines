# coding=utf-8

import pytest
from flask import Response, json
from flask.testing import FlaskClient

from skylines.model import User, Club, Airport


@pytest.fixture(autouse=True)
def fixtures(db_session):
    db_session.add(User(first_name=u'John', last_name=u'Doe', password='jane123'))
    db_session.add(User(first_name=u'Jane', last_name=u'Doe', password='johnny'))
    db_session.add(Club(name=u'LV Aachen', website='https://www.lv-aachen.de'))
    db_session.add(Club(name=u'Sportflug Niederberg'))
    db_session.add(Airport(name=u'Aachen-Merzbrück', country_code='DE', icao='EDKA', frequency='122.875'))
    db_session.add(Airport(name=u'Meiersberg', country_code='DE'))
    db_session.commit()


def test_search(client, default_headers):
    assert isinstance(client, FlaskClient)

    response = client.get('/search?q=aachen', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == [{
        'type': 'airport',
        'id': 1,
        'name': u'Aachen-Merzbrück',
        'icao': 'EDKA',
        'frequency': '122.875',
    }, {
        'type': 'club',
        'id': 1,
        'name': u'LV Aachen',
        'website': 'https://www.lv-aachen.de',
    }]


def test_search2(client, default_headers):
    assert isinstance(client, FlaskClient)

    response = client.get('/search?q=doe', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == [{
        'type': 'user',
        'id': 4,
        'name': u'Jane Doe',
    }, {
        'type': 'user',
        'id': 3,
        'name': u'John Doe',
    }]


def test_missing_search_text(client, default_headers):
    assert isinstance(client, FlaskClient)

    response = client.get('/search', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 422

    data = json.loads(response.data)
    assert data == {'messages': {'q': ['Missing data for required field.']}}
