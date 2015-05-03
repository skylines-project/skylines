import pytest
from zope.testbrowser.wsgi import Browser

import config
from skylines import create_frontend_app


@pytest.fixture(scope="session")
def app():
    """Set up global front-end app for functional tests

    Initialized once per test-run
    """
    return create_frontend_app(config.TESTING_CONF_PATH)


@pytest.fixture(scope="function")
def browser(app):
    """
    A ``zope.testbrowser.wsgi.Browser`` instance for integration testing.
    """
    return Browser('http://localhost/', wsgi_app=app.wsgi_app)
