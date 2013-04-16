# -*- coding: utf-8 -*-
"""Setup the SkyLines application"""

import transaction

from skylines import model


def bootstrap(command, conf, vars):
    """Place any commands to setup skylines here"""

    # <websetup.bootstrap.before.auth>
    from sqlalchemy.exc import IntegrityError
    try:
        u = model.User()
        u.display_name = u'Example manager'
        u.email_address = u'manager@somedomain.com'
        u.password = u'managepass'

        model.DBSession.add(u)

        g = model.Group()
        g.group_name = u'managers'
        g.display_name = u'Managers Group'

        g.users.append(u)

        model.DBSession.add(g)

        p = model.Permission()
        p.permission_name = u'manage'
        p.description = u'This permission give an administrative right to the bearer'
        p.groups.append(g)

        model.DBSession.add(p)

        u1 = model.User()
        u1.display_name = u'Example user'
        u1.email_address = u'max+skylines@blarg.de'
        u1.password = u'test'
        u1.tracking_key = 123456

        model.DBSession.add(u1)

        g1 = model.Group()
        g1.group_name = u'pilots'
        g1.display_name = u'Pilots Group'

        g1.users.append(u1)

        model.DBSession.add(g1)

        p1 = model.Permission()
        p1.permission_name = u'upload'
        p1.description = u'Allow uploading new flights'
        p1.groups.append(g1)

        model.DBSession.add(p)

        model.DBSession.flush()
        transaction.commit()
    except IntegrityError:
        print 'Warning, there was a problem adding your auth data, it may have already been added:'
        import traceback
        print traceback.format_exc()
        transaction.abort()
        print 'Continuing with bootstrapping...'

    # <websetup.bootstrap.after.auth>
