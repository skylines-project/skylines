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
from skylines.lib import app_globals, helpers  # NOQA


base_config = AppConfig()
base_config.renderers = []

base_config.package = skylines

#Enable json in expose
base_config.renderers.append('json')
#Set the default renderer
base_config.default_renderer = 'jinja'
base_config.renderers.append('jinja')
base_config.jinja_extensions = [
    'jinja2.ext.i18n',
    'jinja2.ext.with_',
    'jinja2.ext.do',
    'webassets.ext.jinja2.AssetsExtension',
]


def install_gettext_callables(app):
    from tg import config
    from tg.i18n import ugettext, ungettext
    jinja2_env = config['pylons.app_globals'].jinja2_env
    jinja2_env.install_gettext_callables(ugettext, ungettext)
    jinja2_env.autoescape = False
    return app

base_config.register_hook('after_config', install_gettext_callables)


def install_assets_environment(app):
    from tg import config
    from skylines.assets import Environment

    jinja2_env = config['pylons.app_globals'].jinja2_env

    # Initialize webassets environment
    jinja2_env.assets_environment = Environment(config)

    # Load predefined bundles from YAML file
    jinja2_env.assets_environment.load_bundles(
        config['webassets.bundles_module'])

    return app


base_config.register_hook('after_config', install_assets_environment)

#base_config.renderers.append('mako')
# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')
base_config.use_dotted_templatenames = False

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = model
base_config.DBSession = model.DBSession

# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'

# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = model.User
base_config.sa_auth.translations.user_name = 'email_address'

from tg.configuration.auth import TGAuthMetadata


#This tells to TurboGears how to retrieve the data for your user
class ApplicationAuthMetadata(TGAuthMetadata):
    def __init__(self, sa_auth):
        self.sa_auth = sa_auth

    def get_user(self, identity, userid):
        return self.sa_auth.dbsession.query(self.sa_auth.user_class) \
            .filter_by(**{self.sa_auth.translations.user_name: userid}).first()

    def get_groups(self, identity, userid):
        return [g.group_name for g in identity['user'].groups]

    def get_permissions(self, identity, userid):
        return [p.permission_name for p in identity['user'].permissions]

base_config.sa_auth.dbsession = model.DBSession

base_config.sa_auth.authmetadata = ApplicationAuthMetadata(base_config.sa_auth)


# override this if you would like to provide a different who plugin for
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

# override this if you are using a different charset for the login form
base_config.sa_auth.charset = 'utf-8'

# You may optionally define a page where you want users to be redirected to
# on login:
base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
base_config.sa_auth.post_logout_url = '/post_logout'
