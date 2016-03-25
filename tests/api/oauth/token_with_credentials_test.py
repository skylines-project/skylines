from werkzeug.datastructures import Headers

ORIGIN = 'https://www.google.com'


def test_405_for_get(client):
    assert client.get('/oauth/token').status_code == 405


def test_400_without_grant_type(client):
    headers = Headers()
    headers.set('Origin', ORIGIN)

    response = client.post('/oauth/token', headers=headers)
    assert response.status_code == 400
    assert response.headers.get('Access-Control-Allow-Origin') == ORIGIN
    assert response.headers.get('Access-Control-Allow-Credentials') == 'true'
    assert response.json.get('error') == 'unsupported_grant_type'


def test_400_with_unsupported_grant_type(client):
    response = client.post('/oauth/token', data={'grant_type': 'implicit'})
    assert response.status_code == 400
    assert response.json.get('error') == 'unsupported_grant_type'


def test_password_400_without_credentials(client):
    response = client.post('/oauth/token', data={'grant_type': 'password'})
    assert response.status_code == 400
    assert response.json.get('error') == 'invalid_request'


def test_password_401_with_wrong_credentials(client):
    response = client.post('/oauth/token', data={
        'grant_type': 'password',
        'username': 'wrong-username',
        'password': 'wrong-password',
    })
    assert response.status_code == 401
    assert response.json.get('error') == 'invalid_grant'


def test_password_200_with_correct_credentials(client):
    response = client.post('/oauth/token', data={
        'grant_type': 'password',
        'username': 'test@foo.com',
        'password': 'secret123',
    })
    assert response.status_code == 200
    assert response.json.get('access_token')
    assert response.json.get('expires_in')
    assert response.json.get('token_type') == 'Bearer'
    assert response.json.get('refresh_token')
