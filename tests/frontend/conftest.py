import pytest
from zope.testbrowser.wsgi import Browser

import config
from skylines import create_frontend_app
from tests import setup_app, setup_db, teardown_db


@pytest.yield_fixture(scope="session")
def app():
    """Set up global front-end app for functional tests

    Initialized once per test-run
    """
    app = create_frontend_app(config.TESTING_CONF_PATH)
    with app.app_context():
        setup_app(app)
        setup_db()
        yield app
        teardown_db()


@pytest.yield_fixture(scope="function")
def browser(app):
    """
    A ``zope.testbrowser.wsgi.Browser`` instance for integration testing.
    """
    yield Browser('http://localhost/', wsgi_app=app.wsgi_app)
