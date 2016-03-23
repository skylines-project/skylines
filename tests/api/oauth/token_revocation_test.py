def test_400_with_missing_token(client):
    response = client.post('/oauth/revoke')
    assert response.status_code == 400
    assert response.json.get('error') == 'invalid_request'


def test_200_with_unknown_token(client):
    response = client.post('/oauth/revoke', data={'token': 'invalid-token'})
    assert response.status_code == 200


def test_200_with_valid_refresh_token(client, refresh_token):
    response = client.post('/oauth/token', data={'grant_type': 'refresh_token', 'refresh_token': refresh_token})
    assert response.status_code == 200
    assert response.json.get('access_token')
    assert response.json.get('expires_in')
    assert response.json.get('token_type') == 'Bearer'
    assert response.json.get('refresh_token') == refresh_token

    response = client.post('/oauth/revoke', data={'token': refresh_token})
    assert response.status_code == 200

    response = client.post('/oauth/token', data={'grant_type': 'refresh_token', 'refresh_token': refresh_token})
    assert response.status_code == 401
    assert response.json.get('error') == 'invalid_grant'
