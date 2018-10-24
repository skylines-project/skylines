from datetime import datetime

from skylines.lib.xcsoar_ import FlightPathFix

from pytest import approx


def test_list_to_fix():
    values = [
        datetime(2016, 5, 4, 8, 10, 50),
        29450,
        dict(latitude=50.82191666668235, longitude=6.181650000001908),
        230,
        48,
        None,
        None,
        0,
        None,
        None,
        8,
        None,
        0,
    ]

    fix = FlightPathFix(*values)
    assert fix.datetime.isoformat() == "2016-05-04T08:10:50"
    assert fix.seconds_of_day == 29450
    assert fix.location["latitude"] == approx(50.82191666668235)
    assert fix.location["longitude"] == approx(6.181650000001908)
    assert fix.gps_altitude == 230
    assert fix.pressure_altitude == 48
    assert fix.enl == None
    assert fix.track == None
    assert fix.groundspeed == 0
    assert fix.tas == None
    assert fix.ias == None
    assert fix.siu == 8
    assert fix.elevation == None


def test_kwargs():
    fix = FlightPathFix(
        datetime=datetime(2016, 5, 4, 8, 10, 50),
        seconds_of_day=29450,
        location=dict(latitude=50.82191666668235, longitude=6.181650000001908),
        gps_altitude=230,
        pressure_altitude=48,
        groundspeed=0,
        siu=8,
    )

    assert fix.datetime.isoformat() == "2016-05-04T08:10:50"
    assert fix.seconds_of_day == 29450
    assert fix.location["latitude"] == approx(50.82191666668235)
    assert fix.location["longitude"] == approx(6.181650000001908)
    assert fix.gps_altitude == 230
    assert fix.pressure_altitude == 48
    assert fix.enl == None
    assert fix.track == None
    assert fix.groundspeed == 0
    assert fix.tas == None
    assert fix.ias == None
    assert fix.siu == 8
    assert fix.elevation == None
