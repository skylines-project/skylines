#!/usr/bin/python
#
# A interactive shell for inspecting the SkyLines data model.
#

import sys, os
from paste.deploy.loadwsgi import appconfig
from IPython.config.loader import Config
from IPython.frontend.terminal.embed import InteractiveShellEmbed
from skylines.config.environment import load_environment
from skylines.model import *

sys.path.append(os.path.dirname(sys.argv[0]))

conf_path = '/etc/skylines/production.ini'
if len(sys.argv) > 1:
    conf_path = sys.argv[1]
conf = appconfig('config:' + os.path.abspath(conf_path))
load_environment(conf.global_conf, conf.local_conf)

config = Config()
shell = InteractiveShellEmbed(config=config)
shell.push(globals())
shell('SkyLines Shell')
