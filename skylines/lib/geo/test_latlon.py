"""
Unit tests for the LatLon class
"""

from nose.tools import assert_equal, assert_raises
from latlon import LatLon


def test_valid():
    """
    Test valid LatLon
    """

    p = LatLon(51, 7)
    assert_equal(p.latitude, 51.0)
    assert_equal(p.longitude, 7.0)

    p = LatLon(-51, 7)
    assert_equal(p.latitude, -51.0)
    assert_equal(p.longitude, 7.0)

    p = LatLon(51, -7)
    assert_equal(p.latitude, 51.0)
    assert_equal(p.longitude, -7.0)


def test_invalid():
    """
    Test invalid LatLon
    """

    p = LatLon(151, 7)
    assert_equal(p.latitude, 151.0)
    assert_equal(p.longitude, 7.0)

    p = LatLon(-51, 700)
    assert_equal(p.latitude, -51.0)
    assert_equal(p.longitude, 700.0)


def test_exceptions():
    """
    Test exceptions
    """

    assert_raises(ValueError, LatLon, 91, 7, True)
    assert_raises(ValueError, LatLon, 51, 181, True)
    assert_raises(ValueError, LatLon, -91, 7, True)
    assert_raises(ValueError, LatLon, 51, -181, True)


def test_strings():
    """
    Test string conversion
    """

    p = LatLon(51, 7)
    assert_equal(str(p), "+51.00000, +007.00000")

    p = LatLon(-51, -7)
    assert_equal(str(p), "-51.00000, -007.00000")

    p = LatLon(51.123456, 7.987654)
    assert_equal(str(p), "+51.12346, +007.98765")
