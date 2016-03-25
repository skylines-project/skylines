import base64

from flask import Response
from flask.testing import FlaskClient
import pytest

import config
from skylines.api.oauth import oauth
from skylines.app import SkyLines
from skylines.database import db as _db

pytestmark = pytest.mark.usefixtures('db')


@pytest.fixture(scope='session')
def app():
    app = SkyLines(config_file=config.TESTING_CONF_PATH)
    _db.init_app(app)

    oauth.init_app(app)

    @app.route('/')
    @oauth.require_oauth()
    def index():
        return 'success'

    return app


def test_access_denied_without_authorization(client, default_headers):
    assert isinstance(client, FlaskClient)

    response = client.get('/', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 401


def test_access_denied_with_wrong_authorization(client, default_headers):
    assert isinstance(client, FlaskClient)

    default_headers['Authorization'] = 'Basic ' + base64.b64encode('test:password')

    response = client.get('/', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 401


def test_access_granted_with_correct_authorization(client, default_headers, test_user):
    assert isinstance(client, FlaskClient)

    default_headers['Authorization'] = 'Basic ' + base64.b64encode(
        test_user.email_address + ':' + test_user.original_password
    )

    response = client.get('/', headers=default_headers)
    assert isinstance(response, Response)
    assert response.status_code == 200
