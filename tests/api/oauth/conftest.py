import pytest
from werkzeug.datastructures import Headers

from flask import jsonify, request

import config
from skylines.api.cors import cors
from skylines.api.oauth import oauth
from skylines.app import SkyLines
from skylines.model import User
from skylines.database import db as _db

ORIGIN = 'https://www.google.com'


@pytest.fixture(scope='session')
def app():
    app = SkyLines(config_file=config.TESTING_CONF_PATH)
    _db.init_app(app)

    oauth.init_app(app)
    cors.init_app(app)

    @app.route('/secrets')
    @oauth.required()
    def secrets():
        return jsonify({'secrets': [1, 1, 2, 3, 5, 8, 13]})

    @app.route('/user')
    @oauth.optional()
    def user():
        return jsonify({'user': request.user_id})

    return app


@pytest.yield_fixture(scope='session')
def db(app):
    _db.app = app
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture(scope='session')
def test_user(db):
    user = User(email_address='test@foo.com', password='secret123', first_name='test')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def tokens(client, test_user):
    headers = Headers()
    headers.set('Origin', ORIGIN)

    response = client.post('/oauth/token', headers=headers, data={
        'grant_type': 'password',
        'username': 'test@foo.com',
        'password': 'secret123',
    })
    assert response.status_code == 200
    assert response.headers.get('Access-Control-Allow-Origin') == ORIGIN
    assert response.headers.get('Access-Control-Allow-Credentials') == 'true'
    assert response.json.get('access_token')
    assert response.json.get('expires_in')
    assert response.json.get('token_type') == 'Bearer'
    assert response.json.get('refresh_token')

    return response.json


@pytest.fixture
def access_token(tokens):
    return tokens.get('access_token')


@pytest.fixture
def refresh_token(tokens):
    return tokens.get('refresh_token')
