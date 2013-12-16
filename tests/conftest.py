import pytest
from tests.data.bootstrap import bootstrap as _bootstrap

import config
from skylines.app import create_app
from skylines.model import db as _db


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""

    app = create_app(config_file=config.TESTING_CONF_PATH)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""

    _db.create_all()

    def teardown():
        _db.drop_all()
        _db.session.remove()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def bootstrap(db, request):
    _bootstrap()

    def teardown():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())

        db.session.commit()

    request.addfinalizer(teardown)
