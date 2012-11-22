# -*- coding: utf-8 -*-
"""Functional test suite for the controllers of the application."""

from skylines.tests import setup_app, teardown_db
from skylines import model

def setup():
    # Setup the database
    setup_app()

    # Remove the current session
    # The TestController creates his own sessions
    model.DBSession.remove()


def teardown():
    # Remove the database again
    teardown_db()
