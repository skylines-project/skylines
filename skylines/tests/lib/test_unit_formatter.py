import sys
import nose
from nose.tools import eq_

from flask import g
from skylines import app
import skylines.lib.formatter.units as units


def setup():
    app.add_babel()
    app.test_request_context().push()
    g.current_user = None


def test_distance_format():
    """ Check distance formatting """

    eq_(units.format_distance(0), '0 km')
    eq_(units.format_distance(1234000), '1234 km')

    eq_(units.format_distance(25, 2), '0.03 km')
    eq_(units.format_distance(2500, 2), '2.50 km')
    eq_(units.format_distance(1234000, 2), '1234.00 km')


def test_speed_format():
    """ Check speed formatting """

    eq_(units.format_speed(0), '0.0 km/h')
    eq_(units.format_speed(12), '43.2 km/h')
    eq_(units.format_speed(10, 3), '36.000 km/h')


def test_lift_format():
    """ Check lift formatting """

    eq_(units.format_lift(0), '0.0 m/s')
    eq_(units.format_lift(4.3), '4.3 m/s')
    eq_(units.format_lift(10, 3), '10.000 m/s')


def test_altitude_format():
    """ Check altitude formatting """

    eq_(units.format_altitude(-10), '-10 m')
    eq_(units.format_altitude(0), '0 m')
    eq_(units.format_altitude(432), '432 m')
    eq_(units.format_altitude(10, 1), '10.0 m')


if __name__ == "__main__":
    sys.argv.append(__name__)
    nose.run()
