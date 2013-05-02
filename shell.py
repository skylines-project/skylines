#!/usr/bin/python
#
# A interactive shell for inspecting the SkyLines data model.
#

import sys
import os
from paste.deploy.loadwsgi import appconfig
from IPython.config.loader import Config
from IPython.frontend.terminal.embed import InteractiveShellEmbed
from skylines.config.environment import load_environment
from skylines.model import *

sys.path.append(os.path.dirname(sys.argv[0]))

PRO_CONF_PATH = '/etc/skylines/production.ini'
DEV_CONF_PATH = 'development.ini'

if len(sys.argv) > 1:
    conf_path = sys.argv[1]
    if not os.path.exists(conf_path):
        parser.error('Config file "{}" not found.'.format(conf_path))
elif os.path.exists(PRO_CONF_PATH):
    conf_path = PRO_CONF_PATH
else:
    conf_path = DEV_CONF_PATH

conf = appconfig('config:' + os.path.abspath(conf_path))
load_environment(conf.global_conf, conf.local_conf)

config = Config()
shell = InteractiveShellEmbed(config=config)
shell.push(globals())
shell('SkyLines Shell')
