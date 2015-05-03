# -*- coding: utf-8 -*-
import pytest

from skylines.model import db, User

attrs = dict(
    email_address=u"ignucius@example.org",
    first_name=u"Test",
    last_name=u"User",
    password="something"
)


@pytest.fixture(scope='function')
def test_user(db_session):
    obj = User(**attrs)
    db_session.add(obj)
    db_session.commit()
    return obj


def test_obj_creation_email(test_user):
    """The obj constructor must set the email right"""
    assert test_user.email_address == u"ignucius@example.org"


def test_no_permissions_by_default(test_user):
    """User objects should have no permission by default."""
    assert test_user.admin == False


def test_getting_by_email(test_user):
    """Users should be fetcheable by their email addresses"""
    him = User.by_email_address(u"ignucius@example.org")
    assert him == test_user


def test_query_obj(test_user):
    """Model objects can be queried"""
    obj = db.session.query(User).one()

    assert obj == test_user
    assert obj.email_address == attrs.get('email_address')
    assert obj.first_name == attrs.get('first_name')
    assert obj.last_name == attrs.get('last_name')
