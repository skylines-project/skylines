from werkzeug.datastructures import Headers

ORIGIN = 'https://www.google.com'


def test_no_cors(client):
    response = client.get('/')
    assert 'Access-Control-Allow-Origin' not in response.headers
    assert 'Access-Control-Allow-Credentials' not in response.headers
    assert 'Access-Control-Allow-Methods' not in response.headers
    assert 'Access-Control-Allow-Headers' not in response.headers


def test_cors(client):
    headers = Headers()
    headers.set('Origin', ORIGIN)

    response = client.get('/', headers=headers)
    assert response.headers.get('Access-Control-Allow-Origin') == ORIGIN
    assert response.headers.get('Access-Control-Allow-Credentials') == 'true'
    assert 'Access-Control-Allow-Methods' not in response.headers
    assert 'Access-Control-Allow-Headers' not in response.headers


def test_cors_with_headers(client):
    headers = Headers()
    headers.set('Origin', ORIGIN)
    headers.set('Access-Control-Request-Headers', 'Authorization')

    response = client.get('/', headers=headers)
    assert response.headers.get('Access-Control-Allow-Origin') == ORIGIN
    assert response.headers.get('Access-Control-Allow-Credentials') == 'true'
    assert 'Access-Control-Allow-Methods' not in response.headers
    assert response.headers.get('Access-Control-Allow-Headers') == 'Authorization'


def test_cors_with_methods(client):
    headers = Headers()
    headers.set('Origin', ORIGIN)
    headers.set('Access-Control-Request-Methods', 'get, post')

    response = client.get('/', headers=headers)
    assert response.headers.get('Access-Control-Allow-Origin') == ORIGIN
    assert response.headers.get('Access-Control-Allow-Credentials') == 'true'
    assert response.headers.get('Access-Control-Allow-Methods') == 'get, post'
    assert 'Access-Control-Allow-Headers' not in response.headers
