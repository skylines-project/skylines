import pytest

import config
from zope.testbrowser.wsgi import Browser
from skylines.app import create_frontend_app


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""

    app = create_frontend_app(config_file=config.TESTING_CONF_PATH)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='function')
def browser(app, request):
    #from time import time; t1 = time()
    b = Browser('http://localhost/', wsgi_app=app.wsgi_app)
    #t2 = time(); print 'dt = %f' % (t2-t1)
    return b
