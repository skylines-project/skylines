# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""
from nose.tools import eq_

from skylines import model
from tests.models import ModelTest


class TestUser(ModelTest):
    """Unit test case for the ``User`` model."""

    klass = model.User
    attrs = dict(
        email_address=u"ignucius@example.org",
        first_name=u"Test",
        last_name=u"User",
    )

    def test_obj_creation_email(self):
        """The obj constructor must set the email right"""
        eq_(self.obj.email_address, u"ignucius@example.org")

    def test_no_permissions_by_default(self):
        """User objects should have no permission by default."""
        eq_(self.obj.admin, False)

    def test_getting_by_email(self):
        """Users should be fetcheable by their email addresses"""
        him = model.User.by_email_address(u"ignucius@example.org")
        eq_(him, self.obj)
