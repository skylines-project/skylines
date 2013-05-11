# -*- coding: utf-8 -*-
"""WSGI environment setup for SkyLines."""

import os
from paste.deploy.loadwsgi import appconfig
from .app_cfg import base_config

__all__ = ['load_environment']

PRO_CONF_PATH = '/etc/skylines/production.ini'
DEV_CONF_PATH = 'config/development.ini'


#Use base_config to setup the environment loader function
load_environment = base_config.make_load_environment()


def load_from_file(path=None):
    """
    Loads the application configuration from a file into the environment.
    Returns the configuration or None if no configuration could be found.
    """

    if path:
        if not os.path.exists(path):
            return
    elif os.path.exists(PRO_CONF_PATH):
        path = PRO_CONF_PATH
    elif os.path.exists(DEV_CONF_PATH):
        path = DEV_CONF_PATH
    else:
        return

    conf = appconfig('config:' + os.path.abspath(path))
    load_environment(conf.global_conf, conf.local_conf)
    return conf
