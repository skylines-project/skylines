from flask.ext.script import Command

import sys
from skylines.tracking.server import TrackingServer


class Server(Command):
    """ Runs the live tracking UDP server """

    def run(self):
        from twisted.python import log
        log.startLogging(sys.stdout)

        from twisted.internet import reactor

        reactor.listenUDP(5597, TrackingServer())
        reactor.run()
