# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in SkyLines.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::

    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))

"""

from tg.configuration import AppConfig

import skylines
from skylines import model

# unused here, but needed by TurboGears2
from skylines.lib import app_globals, helpers


base_config = AppConfig()
base_config.renderers = []

base_config.package = skylines

#Enable json in expose
base_config.renderers.append('json')
#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')

base_config.renderers.append('jinja')
base_config.jinja_extensions = ['jinja2.ext.i18n', 'jinja2.ext.with_']

def install_gettext_callables(app):
    from tg.i18n import ugettext, ungettext
    jinja2_env = app_globals.config['pylons.app_globals'].jinja2_env
    jinja2_env.install_gettext_callables(ugettext, ungettext)
    return app

base_config.register_hook('after_config', install_gettext_callables)

#base_config.renderers.append('mako')
# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')
base_config.use_dotted_templatenames = False

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = skylines.model
base_config.DBSession = skylines.model.DBSession
# Configure the authentication backend


base_config.auth_backend = 'sqlalchemy'
base_config.sa_auth.dbsession = model.DBSession

# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = model.User
# what is the class you want to use to search for groups in the database
base_config.sa_auth.group_class = model.Group
# what is the class you want to use to search for permissions in the database
base_config.sa_auth.permission_class = model.Permission

# override this if you would like to provide a different who plugin for
# managing login and logout of your application
base_config.sa_auth.form_plugin = None
base_config.sa_auth.translations.user_name = 'email_address'

# override this if you are using a different charset for the login form
base_config.sa_auth.charset = 'utf-8'

# You may optionally define a page where you want users to be redirected to
# on login:
base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
base_config.sa_auth.post_logout_url = '/post_logout'
