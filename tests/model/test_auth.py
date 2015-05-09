# -*- coding: utf-8 -*-

from skylines.database import db
from skylines.model import User


def test_no_permissions_by_default(test_user):
    """User objects should have no permission by default."""
    assert test_user.admin == False


def test_getting_by_email(test_user):
    """Users should be fetcheable by their email addresses"""
    him = User.by_email_address(test_user.email_address)
    assert him == test_user


def test_query_obj(test_user):
    """Model objects can be queried"""
    obj = db.session.query(User).one()

    assert obj == test_user
    assert obj.email_address == test_user.email_address
    assert obj.first_name == test_user.first_name
    assert obj.last_name == test_user.last_name
