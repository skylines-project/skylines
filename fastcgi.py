#!/usr/bin/python
#
# Wrapper script for launching Skylines as a FastCGI in lighttpd.
#

import sys, os
import thread
import argparse
import logging
from paste.deploy import loadapp
from flup.server.fcgi import WSGIServer

parser = argparse.ArgumentParser(description='Run the SkyLines FastCGI daemon.')
parser.add_argument('config_file', nargs='?', metavar='config.ini',
                    default='/etc/skylines/production.ini',
                    help='path to the configuration INI file')
parser.add_argument('--logfile', nargs='?', metavar='PATH',
                    help='path of the log file')
args = parser.parse_args()

# stderr doesn't work with FastCGI; the following is a hack to get a
# log file with diagnostics anyway
if args.logfile:
    sys.stderr = sys.stdout = file(args.logfile, 'a')

prev_sys_path = list(sys.path)

new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

sys.path.append(os.path.dirname(sys.argv[0]))

thread.stack_size(524288)

wsgi_app = loadapp('config:' + os.path.abspath(args.config_file))
logging.config.fileConfig(args.config_file)

if __name__ == '__main__':
    WSGIServer(wsgi_app, minSpare=1, maxSpare=5, maxThreads=50).run()
