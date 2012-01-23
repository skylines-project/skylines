"""Unit tests for the IGCWriter class"""

from nose.tools import assert_equal, raises
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


@raises(ValueError)
def test_exception():
    """
    Test exception 1
    """

    LatLon(91, 7, True)


@raises(ValueError)
def test_exception2():
    """
    Test exception 2
    """

    LatLon(51, 181, True)


@raises(ValueError)
def test_exception3():
    """
    Test exception 3
    """

    LatLon(-91, 7, True)


@raises(ValueError)
def test_exception4():
    """
    Test exception 4
    """

    LatLon(51, -181, True)
