#!/usr/bin/env python
#
# Generate fake live tracks for debugging.
#

import sys
import os
import argparse
from config import to_envvar

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Generate fake live tracks for debugging.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')
parser.add_argument('user', type=int,
                    help='a user ID')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))

import sys
from math import sin
from random import randint
from time import sleep
from skylines import db
from skylines.model import TrackingFix


i = randint(0, 100)
_longitude = randint(6500, 7500) / 1000.
_latitude = randint(50500, 51500) / 1000.
_altitude = 500

while True:
    longitude = sin(i / 73.) * 0.001 + _longitude
    latitude = sin(i / 50.) * 0.004 + _latitude
    altitude = sin(i / 20.) * 300 + _altitude

    fix = TrackingFix()
    fix.pilot_id = args.user
    fix.set_location(longitude, latitude)
    fix.altitude = altitude

    db.session.add(fix)
    db.session.commit()

    print '.',
    sys.stdout.flush()

    sleep(1)

    i += 1
