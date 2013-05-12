#!/usr/bin/env python
#
# The SkyLines daemon, responsible for live tracking (and maybe other
# Twisted applications).
#

import sys
import os
import argparse
from skylines.config import environment

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Run the SkyLines Live Tracking daemon.')
parser.add_argument('conf_path', nargs='?', metavar='config.ini',
                    help='path to the configuration INI file')

args = parser.parse_args()

if not environment.load_from_file(args.conf_path):
    parser.error('Config file "{}" not found.'.format(args.conf_path))

if __name__ == '__main__':
    from twisted.python import log
    log.startLogging(sys.stdout)

    from twisted.internet import reactor
    from skylines.tracking.server import TrackingServer
    reactor.listenUDP(5597, TrackingServer())
    reactor.run()
