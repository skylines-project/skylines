def test_400_with_missing_refresh_token(client):
    response = client.post('/oauth/token', data={'grant_type': 'refresh_token'})
    assert response.status_code == 400
    assert response.json.get('error') == 'invalid_request'


def test_401_with_invalid_refresh_token(client):
    response = client.post('/oauth/token', data={'grant_type': 'refresh_token', 'refresh_token': 'invalid-token'})
    assert response.status_code == 401
    assert response.json.get('error') == 'invalid_grant'


def test_200_with_valid_refresh_token(client, refresh_token):
    response = client.post('/oauth/token', data={'grant_type': 'refresh_token', 'refresh_token': refresh_token})
    assert response.status_code == 200
    assert response.json.get('access_token')
    assert response.json.get('expires_in')
    assert response.json.get('token_type') == 'Bearer'
    assert response.json.get('refresh_token') == refresh_token
