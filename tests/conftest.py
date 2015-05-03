import random
import pytest

import config
from skylines import model, create_app
from skylines.app import SkyLines

from tests import setup_db, teardown_db, clean_db
from tests.data import users


@pytest.fixture(scope="function")
def seeded_random():
    """
    Calls random.seed() with a constant to ensure that random always returns
    the same results.
    """

    random.seed(1234)


@pytest.yield_fixture(scope="session")
def app():
    """Global skylines application fixture

    Initialized with testing config file.
    """
    yield create_app(config_file=config.TESTING_CONF_PATH)


@pytest.yield_fixture(scope="session")
def db_schema(app):
    """Creates clean database schema and drops it on teardown

    Note, that this is a session scoped fixture, it will be executed only once
    and shared among all tests. Use `db` fixture to get clean database before
    each test.
    """
    assert isinstance(app, SkyLines)

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
    assert isinstance(app, SkyLines)

    with app.app_context():
        clean_db()
        yield db_schema
        db_schema.rollback()


@pytest.yield_fixture(scope="function")
def test_admin(db):
    """
    Creates a test admin
    """
    user = users.test_admin()
    db.add(user)
    db.commit()
    yield user


@pytest.yield_fixture(scope="function")
def test_user(db):
    """
    Creates a single test user
    """
    user = users.test_user()
    db.add(user)
    db.commit()
    yield user
