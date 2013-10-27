# -*- coding: utf-8 -*-
"""Setup the SkyLines application"""

from skylines import model, db


def bootstrap():
    from sqlalchemy.exc import IntegrityError
    try:
        u = model.User()
        u.name = u'Example manager'
        u.email_address = u'manager@somedomain.com'
        u.password = u'managepass'

        db.session.add(u)

        g = model.Group()
        g.group_name = u'managers'
        g.name = u'Managers Group'

        g.users.append(u)

        db.session.add(g)

        p = model.Permission()
        p.permission_name = u'manage'
        p.description = u'This permission give an administrative right to the bearer'
        p.groups.append(g)

        db.session.add(p)

        u1 = model.User()
        u1.name = u'Example user'
        u1.email_address = u'max+skylines@blarg.de'
        u1.password = u'test'
        u1.tracking_key = 123456

        db.session.add(u1)

        g1 = model.Group()
        g1.group_name = u'pilots'
        g1.name = u'Pilots Group'

        g1.users.append(u1)

        db.session.add(g1)

        p1 = model.Permission()
        p1.permission_name = u'upload'
        p1.description = u'Allow uploading new flights'
        p1.groups.append(g1)

        db.session.add(p)

        db.session.commit()
    except IntegrityError:
        print 'Warning, there was a problem adding your auth data, it may have already been added:'
        import traceback
        print traceback.format_exc()
        db.session.rollback()
        print 'Continuing with bootstrapping...'
