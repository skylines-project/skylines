# -*- coding: utf-8 -*-
"""Setup the SkyLines application"""
from faker import Faker

from skylines.model import User


def test_admin():
    u = User()
    u.first_name = u'Example'
    u.last_name = u'Manager'
    u.email_address = u'manager@somedomain.com'
    u.password = u.original_password = u'managepass'
    u.admin = True
    return u


def test_user():
    u1 = User()
    u1.first_name = u'Example'
    u1.last_name = u'User'
    u1.email_address = u'example@test.de'
    u1.password = u1.original_password = u'test'
    u1.tracking_key = 123456
    return u1


def test_users(n=50):
    fake = Faker(locale='de_DE')
    fake.seed(42)

    users = []
    for i in xrange(n):
        u = User()
        u.first_name = fake.first_name()
        u.last_name = fake.last_name()
        u.email_address = fake.email()
        u.password = u.original_password = fake.password()
        u.tracking_key = fake.random_number(digits=6)

        users.append(u)

    return users
