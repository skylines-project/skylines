from flask.ext.script import Command, Option

import sys
import socket
import struct
from skylines.model import User
from skylines.tracking.server import *  # noqa
from math import sin
from random import randint
from time import sleep


class GenerateThroughDaemon(Command):
    """ Generate fake live tracks for debugging on daemon """

    UDP_IP = '127.0.0.1'
    UDP_PORT = 5597
    ADDRESS = (UDP_IP, UDP_PORT)

    option_list = (
        Option('user_id', type=int, help='a user ID'),
    )

    def run(self, user_id):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        user = User.get(user_id)
        if not user:
            print 'User with id "{}" not found.'.format(user_id)
            sys.exit(1)

        start_time = datetime.utcnow()

        i = randint(0, 100)
        _time = (start_time.hour * 60 * 60 * 1000 +
                 start_time.minute * 60 * 1000 +
                 start_time.second * 1000)
        _longitude = randint(6500, 7500) / 1000.
        _latitude = randint(50500, 51500) / 1000.
        _altitude = 500

        while True:
            longitude = sin(i / 73.) * 0.001 + _longitude
            latitude = sin(i / 50.) * 0.004 + _latitude
            altitude = sin(i / 20.) * 300 + _altitude

            flags = FLAG_LOCATION | FLAG_ALTITUDE
            fix = TrackingFix()
            fix.pilot_id = user.id
            fix.set_location(longitude, latitude)
            fix.altitude = altitude

            data = struct.pack(
                '!IHHQIIiiIHHHhhH',
                MAGIC,
                0,
                TYPE_FIX,
                user.tracking_key,
                flags,
                _time,
                int(latitude * 1000000),
                int(longitude * 1000000),
                0,
                0,
                0,
                0,
                altitude,
                0,
                0,
            )
            data = set_crc(data)
            sock.sendto(data, self.ADDRESS)

            print '.',
            sys.stdout.flush()

            sleep(1)

            i += 1
            _time += 1000
