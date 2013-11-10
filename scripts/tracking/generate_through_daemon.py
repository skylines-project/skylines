#!/usr/bin/env python
#
# Generate fake live tracks for debugging on daemon.
#

import sys
import os
import argparse
from config import to_envvar

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Generate fake live tracks for debugging on daemon.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')
parser.add_argument('user', type=int,
                    help='a user ID')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))

import sys
import socket
import struct
from skylines.model import User
from skylines.tracking.server import *  # noqa
from math import sin
from random import randint
from time import sleep


UDP_IP = '127.0.0.1'
UDP_PORT = 5597
ADDRESS = (UDP_IP, UDP_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

user = User.get(args.user)
if not user:
    parser.error('User with id "{}" not found.'.format(args.user))

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
    fix.pilot_id = args.user
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
    sock.sendto(data, ADDRESS)

    print '.',
    sys.stdout.flush()

    sleep(1)

    i += 1
    _time += 1000
