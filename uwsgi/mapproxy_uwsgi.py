#!/usr/bin/env python
#
# Wrapper script for launching MapProxy WSGI app.
#

import os
import sys
#import thread
import argparse
from config import to_envvar

parser = argparse.ArgumentParser(description='Run the MapProxy WSGI app.')
parser.add_argument('config_file', nargs='?', metavar='mapproxy.yaml',
                    help='path to the configuration YAML file')
parser.add_argument('--logfile', nargs='?', metavar='PATH',
                    help='path of the log file')
args = parser.parse_args()

if not to_envvar(args.config_file):
    parser.error('Config file "{}" not found.'.format(args.config_file))

# stderr doesn't work with FastCGI; the following is a hack to get a
# log file with diagnostics anyway
#if args.logfile:
#    sys.stderr = sys.stdout = file(args.logfile, 'a')

sys.path.append(os.path.dirname(sys.argv[0]))

#thread.stack_size(524288)

from mapproxy.wsgiapp import make_wsgi_app
application = make_wsgi_app(args.config_file)
