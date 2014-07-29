from flask.ext.script import Command

from skylines.tracking.server import TrackingServer


class Server(Command):
    """ Runs the live tracking UDP server """

    def run(self):
        print 'Receiving datagrams on :5597'
        TrackingServer(':5597').serve_forever()
