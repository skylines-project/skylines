#!/usr/bin/env python
#
# A interactive shell for inspecting the SkyLines data model.
#

import sys
import os
from config import to_envvar

sys.path.append(os.path.dirname(sys.argv[0]))

conf_path = len(sys.argv) > 1 and sys.argv[1]
if not to_envvar(conf_path):
    sys.exit('Config file "{}" not found.'.format(conf_path))


from IPython.config.loader import Config
from IPython.frontend.terminal.embed import InteractiveShellEmbed

from skylines import create_app  # noqa
from skylines.model import *  # noqa

config = Config()
shell = InteractiveShellEmbed(config=config)
shell.push(globals())
shell('SkyLines Shell')
