# -*- coding: utf-8 -*-
"""Unit test suite for the models of the application."""
from tests import AppTest
from skylines.model import db

__all__ = ['ModelTest']


class ModelTest(AppTest):
    """Base unit test case for the models."""

    klass = None
    attrs = {}

    def setup(self):
        """Prepare model test fixture."""
        super(ModelTest, self).setup()

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
            assert getattr(obj, key) == value
