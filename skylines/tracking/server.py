import sys
from twisted.python import log
from twisted.internet import reactor
from skylines.tracking import TrackingProtocol

class Server():
    def __init__(self):
        log.startLogging(sys.stdout)
        reactor.listenUDP(5597, TrackingProtocol())

    def run(self):
        reactor.run()
