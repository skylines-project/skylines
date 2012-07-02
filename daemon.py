#!/usr/bin/python
#
# The SkyLines daemon, responsible for live tracking (and maybe other
# Twisted applications).
#

import sys, os
from paste.deploy.loadwsgi import appconfig
from skylines.config.environment import load_environment

sys.path.append(os.path.dirname(sys.argv[0]))

conf_path = '/etc/skylines/production.ini'
if len(sys.argv) > 1:
    conf_path = sys.argv[1]
    del sys.argv[1]

if len(sys.argv) != 1:
    print >>sys.stderr, "Usage: %s [config.ini]" % sys.argv[0]
    sys.exit(1)

conf = appconfig('config:' + os.path.abspath(conf_path))
load_environment(conf.global_conf, conf.local_conf)

if __name__ == '__main__':
    from twisted.internet import reactor
    from skylines.tracking.server import TrackingServer
    reactor.listenUDP(5597, TrackingServer())
    reactor.run()
