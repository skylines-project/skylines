from __future__ import print_function

from flask_script import Command, Option

import sys
import socket
import struct
from skylines.model import User
from skylines.tracking.server import (
    datetime,
    FLAG_LOCATION,
    FLAG_ALTITUDE,
    MAGIC,
    TYPE_FIX,
    set_crc,
)
from math import sin
from random import randint
from time import sleep


class GenerateThroughDaemon(Command):
    """ Generate fake live tracks for debugging on daemon """

    option_list = (
        Option("--host", type=str, default="127.0.0.1"),
        Option("--port", type=int, default=5597),
        Option("user_id", type=int, help="a user ID"),
    )

    def run(self, user_id, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        user = User.get(user_id)
        if not user:
            print('User with id "{}" not found.'.format(user_id))
            sys.exit(1)

        start_time = datetime.utcnow()

        i = randint(0, 100)
        _time = (
            start_time.hour * 60 * 60 * 1000
            + start_time.minute * 60 * 1000
            + start_time.second * 1000
        )
        _longitude = randint(6500, 7500) / 1000.0
        _latitude = randint(50500, 51500) / 1000.0
        _altitude = 500

        while True:
            longitude = sin(i / 73.0) * 0.001 + _longitude
            latitude = sin(i / 50.0) * 0.004 + _latitude
            altitude = sin(i / 20.0) * 300 + _altitude

            flags = FLAG_LOCATION | FLAG_ALTITUDE

            data = struct.pack(
                "!IHHQIIiiIHHHhhH",
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
                int(altitude),
                0,
                0,
            )
            data = set_crc(data)
            sock.sendto(data, (kwargs.get("host"), kwargs.get("port")))

            print(".", end="")
            sys.stdout.flush()

            sleep(1)

            i += 1
            _time += 1000
