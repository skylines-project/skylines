import pytest
from werkzeug.datastructures import Headers

import config
from skylines import create_api_app


@pytest.fixture(scope="session")
def app():
    """Set up global front-end app for functional tests

    Initialized once per test-run
    """
    app = create_api_app(config.TESTING_CONF_PATH)
    return app


@pytest.yield_fixture
def client(app):
    with app.test_client(use_cookies=False) as client:
        yield client


@pytest.fixture(scope="function")
def default_headers():
    headers = Headers()
    headers.add('User-Agent', 'py.test')
    return headers
