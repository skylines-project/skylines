import logging

from flask.ext.script import Command

from skylines.app import create_app
from skylines.tracking.ogn_gateway import OgnTrackingGateway


class OgnGateway(Command):
    """ Runs the live tracking OpenGliderNetwork gateway """

    def run(self):
        print('Receiving aircraft beacons from OGN')

        logging.basicConfig(level='INFO')
        gateway = OgnTrackingGateway(app=create_app(), aprs_user='skylines', skylines_host='localhost', skylines_port=5597)

        try:
            gateway.run()
        except KeyboardInterrupt:
            print('\nStop ogn-skylines gateway')

        gateway.disconnect()
        logging.shutdown()
