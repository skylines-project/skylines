from __future__ import print_function

from flask_script import Command, Option

import sys
from math import sin
from random import randint
from time import sleep
from datetime import timedelta, datetime

from skylines.database import db
from skylines.model import TrackingFix, User


class Generate(Command):
    """ Generate fake live tracks for debugging """

    option_list = (Option("user_id", type=int, help="a user ID"),)

    def run(self, user_id):
        user = User.get(user_id)
        if not user:
            print('User with id "{}" not found.'.format(user_id))
            sys.exit(1)

        i = randint(0, 100)
        _longitude = randint(6500, 7500) / 1000.0
        _latitude = randint(50500, 51500) / 1000.0
        _altitude = 500

        while True:
            longitude = sin(i / 73.0) * 0.001 + _longitude
            latitude = sin(i / 50.0) * 0.004 + _latitude
            altitude = sin(i / 20.0) * 300 + _altitude

            fix = TrackingFix()
            fix.pilot = user
            fix.set_location(longitude, latitude)
            fix.altitude = altitude
            fix.time = datetime.now()
            fix.time_visible = fix.time + timedelta(minutes=user.tracking_delay)

            db.session.add(fix)
            db.session.commit()

            print(".", end="")
            sys.stdout.flush()

            sleep(1)

            i += 1
