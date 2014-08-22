from flask.ext.script import Command

from skylines.app import create_app
from skylines.tracking.server import TrackingServer


class Server(Command):
    """ Runs the live tracking UDP server """

    def run(self):
        print 'Receiving datagrams on :5597'
        server = TrackingServer(':5597')
        server.init_app(create_app())
        server.serve_forever()
