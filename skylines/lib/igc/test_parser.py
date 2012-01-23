"""
Unit tests for the BaseParser class
"""

from nose.tools import assert_equals, assert_raises, assert_true, assert_false
from parser import BaseParser
from datetime import time as Time
from skylines.lib.geo.latlon import LatLon


def test_parse_time():
    t = BaseParser.parse_time("000000")
    assert_equals(t, Time(0, 0, 0))

    t = BaseParser.parse_time("123456")
    assert_equals(t, Time(12, 34, 56))

    t = BaseParser.parse_time("012345")
    assert_equals(t, Time(01, 23, 45))

    assert_raises(ValueError, BaseParser.parse_time, "")
    assert_raises(ValueError, BaseParser.parse_time, "123")
    assert_raises(ValueError, BaseParser.parse_time, "12345")
    assert_raises(ValueError, BaseParser.parse_time, "1234567")


def test_parse_angle():
    assert_raises(TypeError, BaseParser.parse_angle, "5049380N")
    assert_raises(TypeError, BaseParser.parse_angle, "00611410E")

    a = BaseParser.parse_angle("5049380N", True)
    assert_equals(a, 50 + 49.38 / 60.0)

    a = BaseParser.parse_angle("00611410E", False)
    assert_equals(a, 6 + 11.41 / 60.0)

    a = BaseParser.parse_angle("5049380S", True)
    assert_equals(a, -50 - 49.38 / 60.0)

    a = BaseParser.parse_angle("00611410W", False)
    assert_equals(a, -6 - 11.41 / 60.0)

    assert_raises(ValueError, BaseParser.parse_angle, "5049380", True)
    assert_raises(ValueError, BaseParser.parse_angle, "5049380N", False)
    assert_raises(ValueError, BaseParser.parse_angle, "5049380E", True)
    assert_raises(ValueError, BaseParser.parse_angle, "NNNNNNNN", True)
    assert_raises(ValueError, BaseParser.parse_angle, "00611410", False)
    assert_raises(ValueError, BaseParser.parse_angle, "00611410E", True)
    assert_raises(ValueError, BaseParser.parse_angle, "00611410N", False)
    assert_raises(ValueError, BaseParser.parse_angle, "EEEEEEEEE", False)


def test_parse_latlon():
    l = BaseParser.parse_latlon("5049380N00611410E")
    assert_equals(l, LatLon(50 + 49.38 / 60.0, 6 + 11.41 / 60.0))

    l = BaseParser.parse_latlon("5049380S00611410E")
    assert_equals(l, LatLon(-50 - 49.38 / 60.0, 6 + 11.41 / 60.0))

    l = BaseParser.parse_latlon("5049380S00611410W")
    assert_equals(l, LatLon(-50 - 49.38 / 60.0, -6 - 11.41 / 60.0))

    assert_raises(ValueError, BaseParser.parse_latlon, "5049380N00611410")
    assert_raises(ValueError, BaseParser.parse_latlon, "504S380N00611410E")
    assert_raises(ValueError, BaseParser.parse_latlon, "5049380E00611410E")


def test_parse_fix_validity():
    is_valid = BaseParser.parse_fix_validity("A")
    assert_true(is_valid)

    is_valid = BaseParser.parse_fix_validity("V")
    assert_false(is_valid)

    assert_raises(ValueError, BaseParser.parse_fix_validity, "")
    assert_raises(ValueError, BaseParser.parse_fix_validity, "X")
    assert_raises(ValueError, BaseParser.parse_fix_validity, "1")
    assert_raises(ValueError, BaseParser.parse_fix_validity, "XX")


def test_parse_altitude():
    a = BaseParser.parse_altitude("00000")
    assert_equals(a, 0)

    a = BaseParser.parse_altitude("-0000")
    assert_equals(a, 0)

    a = BaseParser.parse_altitude("99999")
    assert_equals(a, 99999)

    a = BaseParser.parse_altitude("-9999")
    assert_equals(a, -9999)

    assert_raises(ValueError, BaseParser.parse_altitude, "")
    assert_raises(ValueError, BaseParser.parse_altitude, "-99999")
    assert_raises(ValueError, BaseParser.parse_altitude, "123456")
    assert_raises(ValueError, BaseParser.parse_altitude, "1234")
    assert_raises(ValueError, BaseParser.parse_altitude, "undef")


def test_parse_fix():
    a = BaseParser.parse_fix("1010395049380N00611410EA0021200185")
    assert_equals(a.time, Time(10, 10, 39))
    assert_equals(a.latlon, LatLon(50 + 49.38 / 60.0, 6 + 11.41 / 60.0))
    assert_true(a.valid)
    assert_equals(a.baro_altitude, 212)
    assert_equals(a.gps_altitude, 185)

    assert_raises(ValueError, BaseParser.parse_fix, "")


class TestFixHandler(BaseParser):
    def handle_fix(self, fix):
        self.i = self.i + 1

    def test(self):
        self.i = 0
        self.parse(["AFIL01460FLIGHT:1",
                    "B1242215002160N00538980EA0119301199",
                    "LFILORIGIN1007275049380N00611410E",
                    "B1242255002150N00539050EA0120201207",
                    "B1242295002110N00539100EA0120801215",
                    "G1239225E1FFD566DC81EBD308912576110F1F7825DED657F4FDC9"])
        assert_equals(self.i, 3)


class TestNoHandlers(BaseParser):
    def test(self):
        self.parse(["AFIL01460FLIGHT:1",
                    "B1242215002160N00538980EA0119301199",
                    "LFILORIGIN1007275049380N00611410E",
                    "B1242255002150N00539050EA0120201207",
                    "B1242295002110N00539100EA0120801215",
                    "G1239225E1FFD566DC81EBD308912576110F1F7825DED657F4FDC9"])
