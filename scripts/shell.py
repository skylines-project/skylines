#!/usr/bin/env python
#
# A interactive shell for inspecting the SkyLines data model.
#

import sys
import os
import transaction
from IPython.config.loader import Config
from IPython.frontend.terminal.embed import InteractiveShellEmbed
from skylines.config import environment
from skylines.model import *

sys.path.append(os.path.dirname(sys.argv[0]))

conf_path = len(sys.argv) > 1 and sys.argv[1]
if not environment.load_from_file(conf_path):
    sys.exit('Config file "{}" not found.'.format(conf_path))

config = Config()
shell = InteractiveShellEmbed(config=config)
shell.push(globals())
shell.push([transaction])
shell('SkyLines Shell')
