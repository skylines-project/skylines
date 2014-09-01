#!/usr/bin/env python
#
# Wrapper script for launching MapProxy WSGI app.
#

import os
import sys
import argparse
from config import to_envvar

parser = argparse.ArgumentParser(description='Run the MapProxy WSGI app.')
parser.add_argument('config_file', nargs='?', metavar='mapproxy.yaml',
                    help='path to the configuration YAML file')
args = parser.parse_args()

if not to_envvar(args.config_file):
    parser.error('Config file "{}" not found.'.format(args.config_file))

sys.path.append(os.path.dirname(sys.argv[0]))

from mapproxy.wsgiapp import make_wsgi_app
application = make_wsgi_app(args.config_file)
