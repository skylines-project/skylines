from datetime import datetime

from flask import Response, json
from flask.testing import FlaskClient


def test_read_user(client, default_headers, test_user):
    assert isinstance(client, FlaskClient)

    response = client.get('/users/{}'.format(test_user.id), headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200

    json_data = json.loads(response.data)
    assert isinstance(json_data, dict)
    assert json_data['id'] == test_user.id
    assert json_data['name'] == test_user.name
    assert json_data['first_name'] == test_user.first_name
    assert json_data['last_name'] == test_user.last_name
    assert json_data['tracking_call_sign'] is None

    created_at = datetime.strptime(json_data.get('created_at'), "%Y-%m-%dT%H:%M:%S.%f+00:00")
    assert isinstance(created_at, datetime)


def test_read_missing_user(client, default_headers):
    assert isinstance(client, FlaskClient)

    response = client.get('/users/1000000000000', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 404


def test_read_user_with_invalid_id(client, default_headers):
    assert isinstance(client, FlaskClient)

    response = client.get('/users/abc', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 404
