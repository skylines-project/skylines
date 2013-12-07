# -*- coding: utf-8 -*-
"""Unit test suite for the models of the application."""
from nose.tools import assert_equals
from tests import setup_db, teardown_db

import config
from skylines import create_app
from skylines.model import db

__all__ = ['ModelTest']


class ModelTest(object):
    """Base unit test case for the models."""

    klass = None
    attrs = {}

    # Create an empty database before we start our tests for this module
    @classmethod
    def setup_class(cls):
        """Function called by nose on module load"""
        cls.app = create_app(config_file=config.TESTING_CONF_PATH)

        with cls.app.app_context():
            setup_db()

    # Tear down that database
    @classmethod
    def teardown_class(cls):
        """Function called by nose after all tests in this module ran"""
        with cls.app.app_context():
            teardown_db()

    def setUp(self):
        """Prepare model test fixture."""
        self.context = self.app.app_context()
        self.context.push()

        try:
            new_attrs = {}
            new_attrs.update(self.attrs)
            new_attrs.update(self.do_get_dependencies())
            self.obj = self.klass(**new_attrs)
            db.session.add(self.obj)
            db.session.flush()
            return self.obj
        except:
            db.session.rollback()
            raise

    def tearDown(self):
        """Finish model test fixture."""
        db.session.rollback()
        self.context.pop()

    def do_get_dependencies(self):
        """Get model test dependencies.

        Use this method to pull in other objects that need to be created
        for this object to be build properly.

        """
        return {}

    def test_create_obj(self):
        """Model objects can be created"""
        pass

    def test_query_obj(self):
        """Model objects can be queried"""
        obj = db.session.query(self.klass).one()
        for key, value in self.attrs.iteritems():
            assert_equals(getattr(obj, key), value)
