from flask.ext.script import Command, Option

import sys
from math import sin
from random import randint
from time import sleep

from skylines.database import db
from skylines.model import TrackingFix


class Generate(Command):
    """ Generate fake live tracks for debugging """

    option_list = (
        Option('user', type=int, help='a user ID'),
    )

    def run(self, user):

        i = randint(0, 100)
        _longitude = randint(6500, 7500) / 1000.
        _latitude = randint(50500, 51500) / 1000.
        _altitude = 500

        while True:
            longitude = sin(i / 73.) * 0.001 + _longitude
            latitude = sin(i / 50.) * 0.004 + _latitude
            altitude = sin(i / 20.) * 300 + _altitude

            fix = TrackingFix()
            fix.pilot_id = user
            fix.set_location(longitude, latitude)
            fix.altitude = altitude

            db.session.add(fix)
            db.session.commit()

            print '.',
            sys.stdout.flush()

            sleep(1)

            i += 1
