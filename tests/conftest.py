import pytest

import config
from skylines import model, create_app, create_frontend_app

from tests import setup_app, setup_db, teardown_db, clean_db
from tests.data.bootstrap import bootstrap


@pytest.yield_fixture(scope="session")
def app():
    """Global skylines application fixture

    Initialized with testing config file.
    """
    app = create_app(config_file=config.TESTING_CONF_PATH)
    yield app


@pytest.yield_fixture(scope="session")
def db_schema(app):
    """Creates clean database schema and drops it on teardown

    Note, that this is a session scoped fixture, it will be executed only once
    and shared among all tests. Use `db` fixture to get clean database before
    each test.
    """
    with app.app_context():
        setup_db()
        yield model.db.session
        teardown_db()


@pytest.yield_fixture(scope="function")
def db(db_schema, app):
    """Provides clean database before each test. After each test,
    session.rollback() is issued.

    Also, database will be bootstrapped with some initial data.

    Return sqlalchemy session.
    """
    with app.app_context():
        clean_db()
        yield model.db.session
        model.db.session.rollback()


@pytest.yield_fixture(scope="function")
def bootstraped_db(db):
    """Provides clean db, bootstrapped with some initial data  (see
    `tests.bootstrap()`)
    """
    bootstrap()
    yield model.db.session


@pytest.yield_fixture(scope="session")
def frontend_app():
    """Set up global front-end up for functional tests

    Initialized once per test-run
    """
    app = create_frontend_app(config.TESTING_CONF_PATH)
    with app.app_context():
        setup_app(app)
        setup_db()
        yield app
        teardown_db()


@pytest.yield_fixture(scope="function")
def frontend(frontend_app):
    """Clean database before each frontend test

    This fixture uses frontend_app, suitable for functional tests.
    """
    with frontend_app.app_context():
        clean_db()
        bootstrap()
        yield frontend_app
        model.db.session.rollback()
