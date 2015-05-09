# -*- coding: utf-8 -*-
"""Setup the SkyLines application"""

from tests.data.users import test_admin, test_user

from skylines.database import db


def bootstrap():
    from sqlalchemy.exc import IntegrityError
    try:
        db.session.add(test_admin())
        db.session.add(test_user())
        db.session.commit()

    except IntegrityError, e:
        print 'Warning, there was a problem adding your auth data, it may have already been added:', e
        db.session.rollback()
