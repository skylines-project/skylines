import pytest
from flask import Flask, request

from skylines.api.middleware import HTTPMethodOverrideMiddleware


@pytest.fixture
def app():
    test_app = Flask(__name__)
    test_app.wsgi_app = HTTPMethodOverrideMiddleware(test_app.wsgi_app)

    @test_app.route('/', methods=HTTPMethodOverrideMiddleware.allowed_methods)
    def index():
        return request.method

    return test_app


def test_get(client):
    assert client.get('/').data == 'GET'


def test_head(client):
    assert not client.head('/').data


def test_post(client):
    assert client.post('/').data == 'POST'


def test_delete(client):
    assert client.delete('/').data == 'DELETE'


def test_put(client):
    assert client.put('/').data == 'PUT'


def test_patch(client):
    assert client.patch('/').data == 'PATCH'


def test_options(client):
    assert client.options('/').data == 'OPTIONS'


def test_invalid_method(client):
    assert client.open('/', method='INVALID').status.upper() == '405 METHOD NOT ALLOWED'


def test_get_with_head_override(client):
    assert not client.get('/', headers=[('X-HTTP-Method-Override', 'HEAD')]).data


def test_get_with_post_override(client):
    assert client.get('/', headers=[('X-HTTP-Method-Override', 'POST')]).data == 'POST'


def test_get_with_delete_override(client):
    assert client.get('/', headers=[('X-HTTP-Method-Override', 'DELETE')]).data == 'DELETE'


def test_get_with_put_override(client):
    assert client.get('/', headers=[('X-HTTP-Method-Override', 'PUT')]).data == 'PUT'


def test_get_with_patch_override(client):
    assert client.get('/', headers=[('X-HTTP-Method-Override', 'PATCH')]).data == 'PATCH'


def test_get_with_options_override(client):
    assert client.get('/', headers=[('X-HTTP-Method-Override', 'OPTIONS')]).data == 'OPTIONS'


def test_get_with_invalid_method_override(client):
    assert client.open('/', headers=[('X-HTTP-Method-Override', 'INVALID')]).status.upper() == '405 METHOD NOT ALLOWED'
