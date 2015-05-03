import pytest

from flask import g

import skylines.lib.formatter.units as units


@pytest.yield_fixture(scope="module", autouse=True)
def setup_app(app):
    app.add_babel()
    with app.test_request_context():
        g.current_user = None
        yield


def test_distance_format():
    """ Check distance formatting """

    assert units.format_distance(0) == '0 km'
    assert units.format_distance(1234000) == '1234 km'

    assert units.format_distance(25, 2) == '0.03 km'
    assert units.format_distance(2500, 2) == '2.50 km'
    assert units.format_distance(1234000, 2) == '1234.00 km'


def test_speed_format():
    """ Check speed formatting """

    assert units.format_speed(0, 0) == '0 km/h'
    assert units.format_speed(0) == '0.0 km/h'
    assert units.format_speed(12) == '43.2 km/h'
    assert units.format_speed(10, 3) == '36.000 km/h'


def test_lift_format():
    """ Check lift formatting """

    assert units.format_lift(0) == '0.0 m/s'
    assert units.format_lift(4.3) == '4.3 m/s'
    assert units.format_lift(10, 3) == '10.000 m/s'


def test_altitude_format():
    """ Check altitude formatting """

    assert units.format_altitude(-10) == '-10 m'
    assert units.format_altitude(0) == '0 m'
    assert units.format_altitude(432) == '432 m'
    assert units.format_altitude(10, 1) == '10.0 m'
