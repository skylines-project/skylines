from __future__ import division
import socket
import logging

from ogn.client import AprsClient
from ogn.parser import parse_aprs, parse_ogn_beacon, ParseError

from skylines.model import User
from skylines.protocol import create_fix_message

logger = logging.getLogger(__name__)


class OgnTrackingGateway(object):
    def forward_aircraft_beacon(self, beacon):
        pilot = User.by_ogn_address(beacon['address'])
        if not pilot:
            logger.error("BEACON unknown pilot (ogn_address: {:X}".format(beacon['address']))
            return

        logger.info("TRACKED {} {}".format(unicode(pilot).encode('utf8', 'ignore'), beacon['address']))

        message = create_fix_message(pilot.tracking_key,
                                     # NOTE: equivalent is
                                     # (beacon['timestamp'] - beacon['timestamp'].replace(hour=0, minute=0, second=0, microsecond=0)).seconds * 1000
                                     ((beacon['timestamp'].hour * 60 + beacon['timestamp'].minute) * 60 + beacon['timestamp'].second) * 1000,
                                     beacon['latitude'],
                                     beacon['longitude'],
                                     beacon['track'],
                                     beacon['ground_speed'] / 3.6,
                                     0,
                                     int(beacon['altitude']),
                                     beacon['climb_rate'],
                                     0)
        self.socket.sendto(message, self.address)

    def process_beacon(self, raw_message):
        if raw_message[0] == '#':
            return

        try:
            beacon = parse_aprs(raw_message)
            beacon.update(parse_ogn_beacon(beacon['comment']))
        except ParseError as e:
            logger.error(e.message)
            return

        if not beacon['beacon_type'] == 'aircraft_beacon':
            return

        with self.app.app_context():
            self.forward_aircraft_beacon(beacon)

    def __init__(self, app, aprs_user, skylines_host, skylines_port):
        self.app = app
        self.client = AprsClient('skylines')
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM)
        self.address = (skylines_host, skylines_port)

    def run(self):
        self.client.connect()
        self.client.run(callback=self.process_beacon, autoreconnect=True)

    def disconnect(self):
        self.client.disconnect()
