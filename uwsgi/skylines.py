import os
import sys
import config

config.to_envvar()

sys.path.append(os.path.dirname(sys.argv[0]))

from skylines import create_combined_app

application = create_combined_app()
