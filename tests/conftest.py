import os
import random
import shutil

import pytest

import config
from skylines import database, create_app
from skylines.app import SkyLines

from tests import setup_db, teardown_db, clean_db
from tests.data import users, airspace, airports


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


@pytest.fixture(scope="function")
def files_folder(app):
    """
    Creates a clean upload folder
    """
    filesdir = app.config['SKYLINES_FILES_PATH']
    if os.path.exists(filesdir):
        shutil.rmtree(filesdir)

    os.makedirs(filesdir)


@pytest.yield_fixture(scope="session")
def db(app):
    """Creates clean database schema and drops it on teardown

    Note, that this is a session scoped fixture, it will be executed only once
    and shared among all tests. Use `db` fixture to get clean database before
    each test.
    """
    assert isinstance(app, SkyLines)

    setup_db(app)
    yield database.db
    teardown_db()


@pytest.yield_fixture(scope="function")
def db_session(db, app):
    """Provides clean database before each test. After each test,
    session.rollback() is issued.

    Also, database will be bootstrapped with some initial data.

    Return sqlalchemy session.
    """
    assert isinstance(app, SkyLines)

    with app.app_context():
        clean_db()
        yield db.session
        db.session.rollback()


@pytest.fixture(scope="function")
def test_admin(db_session):
    """
    Creates a test admin
    """
    user = users.test_admin()
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def test_user(db_session):
    """
    Creates a single test user
    """
    user = users.test_user()
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def test_users(db_session):
    """
    Creates 50 test users
    """
    _users = users.test_users()
    for user in _users:
        db_session.add(user)
    db_session.commit()
    return _users


@pytest.fixture(scope="function")
def test_airspace(db_session):
    """
    Creates a single test airspace
    """
    test_airspace = airspace.test_airspace()
    db_session.add(test_airspace)
    db_session.commit()
    return test_airspace


@pytest.fixture(scope="function")
def test_airport(db_session):
    """
    Creates a single test airport
    """
    test_airport = airports.test_airport()
    db_session.add(test_airport)
    db_session.commit()
    return test_airport
