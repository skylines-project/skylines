import pytest

import config
from skylines import model, create_frontend_app
from skylines.app import SkyLines
from tests import setup_app, setup_db, teardown_db, clean_db
from tests.data.bootstrap import bootstrap


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
def frontend(app):
    """Clean database before each frontend test

    This fixture uses frontend_app, suitable for functional tests.
    """
    assert isinstance(app, SkyLines)

    with app.app_context():
        clean_db()
        bootstrap()
        yield app
        model.db.session.rollback()
