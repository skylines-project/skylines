from flask import Response, json
from flask.testing import FlaskClient


def test_list_users(client, default_headers, test_users):
    assert isinstance(client, FlaskClient)

    response = client.get('/users/', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200

    json_data = json.loads(response.data)
    assert isinstance(json_data['users'], list)
    assert len(json_data['users']) > 0

    first_user = json_data['users'][0]
    assert isinstance(first_user, dict)
    assert 'id' in first_user
    assert 'name' in first_user


def test_read_user(client, default_headers, test_user):
    assert isinstance(client, FlaskClient)

    response = client.get('/users/{}'.format(test_user.id), headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200

    json_data = json.loads(response.data)
    assert isinstance(json_data, dict)
    assert json_data['id'] == test_user.id
    assert json_data['name'] == test_user.name
    assert json_data['trackingCallsign'] is None


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
