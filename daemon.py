#!/usr/bin/python
#
# The SkyLines daemon, responsible for live tracking (and maybe other
# Twisted applications).
#

import sys
import os
import argparse
from paste.deploy.loadwsgi import appconfig
from skylines.config.environment import load_environment

PRO_CONF_PATH = '/etc/skylines/production.ini'
DEV_CONF_PATH = 'development.ini'

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Run the SkyLines Live Tracking daemon.')
parser.add_argument('conf_path', nargs='?', metavar='config.ini',
                    help='path to the configuration INI file')

args = parser.parse_args()

if args.conf_path is not None:
    if not os.path.exists(args.conf_path):
        parser.error('Config file "{}" not found.'.format(args.conf_path))
elif os.path.exists(PRO_CONF_PATH):
    args.conf_path = PRO_CONF_PATH
else:
    args.conf_path = DEV_CONF_PATH

conf = appconfig('config:' + os.path.abspath(args.conf_path))
load_environment(conf.global_conf, conf.local_conf)

if __name__ == '__main__':
    from twisted.python import log
    log.startLogging(sys.stdout)

    from twisted.internet import reactor
    from skylines.tracking.server import TrackingServer
    reactor.listenUDP(5597, TrackingServer())
    reactor.run()
