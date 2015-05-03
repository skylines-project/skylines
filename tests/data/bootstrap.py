# -*- coding: utf-8 -*-
"""Setup the SkyLines application"""

from skylines.model import db, User


def bootstrap():
    from sqlalchemy.exc import IntegrityError
    try:
        u = User()
        u.first_name = u'Example'
        u.last_name = u'Manager'
        u.email_address = u'manager@somedomain.com'
        u.password = u'managepass'
        u.admin = True

        db.session.add(u)

        u1 = User()
        u1.first_name = u'Example'
        u1.last_name = u'User'
        u1.email_address = u'max+skylines@blarg.de'
        u1.password = u'test'
        u1.tracking_key = 123456

        db.session.add(u1)

        db.session.commit()
    except IntegrityError, e:
        print 'Warning, there was a problem adding your auth data, it may have already been added:', e
        db.session.rollback()
