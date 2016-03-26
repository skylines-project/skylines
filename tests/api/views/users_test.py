from datetime import datetime

from flask import Response, json
from flask.testing import FlaskClient


def test_list_users(client, default_headers, test_users):
    assert isinstance(client, FlaskClient)

    response = client.get('/users/', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200

    json_data = json.loads(response.data)
    assert isinstance(json_data, list)
    assert len(json_data) == 30

    first_user = json_data[0]
    assert isinstance(first_user, dict)
    assert first_user['id'] == test_users[0].id
    assert first_user['name'] == test_users[0].name
    assert first_user['first_name'] == test_users[0].first_name
    assert first_user['last_name'] == test_users[0].last_name
    assert 'tracking_call_sign' not in first_user
    assert 'created_at' not in first_user


def test_list_users_with_pagination(client, default_headers, test_users):
    assert isinstance(client, FlaskClient)

    response = client.get('/users/?per_page=5&page=2', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200

    json_data = json.loads(response.data)
    assert isinstance(json_data, list)
    assert len(json_data) == 5

    third_user = json_data[2]
    assert isinstance(third_user, dict)
    assert third_user['id'] == test_users[7].id
    assert third_user['name'] == test_users[7].name
    assert third_user['first_name'] == test_users[7].first_name
    assert third_user['last_name'] == test_users[7].last_name
    assert 'tracking_call_sign' not in third_user
    assert 'created_at' not in third_user


def test_list_users_with_invalid_page_parameter(client, default_headers):
    assert isinstance(client, FlaskClient)

    response = client.get('/users/?page=abc', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 422

    json_data = json.loads(response.data)
    assert isinstance(json_data, dict)
    assert json_data['messages'] == {'page': ['Not a valid integer.']}


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
