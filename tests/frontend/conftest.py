import pytest
from zope.testbrowser.wsgi import Browser

import config
from skylines import create_frontend_app
from tests import setup_dirs


@pytest.fixture(scope="session")
def app():
    """Set up global front-end app for functional tests

    Initialized once per test-run
    """
    app = create_frontend_app(config.TESTING_CONF_PATH)
    setup_dirs(app)
    return app


@pytest.fixture(scope="function")
def browser(app):
    """
    A ``zope.testbrowser.wsgi.Browser`` instance for integration testing.
    """
    return Browser('http://localhost/', wsgi_app=app.wsgi_app)
