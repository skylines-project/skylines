"""Unit tests for the IGCWriter class"""

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
