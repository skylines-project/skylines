# -*- coding: utf-8 -*-
import pytest

from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon, MultiPolygon

from skylines.model import TimeZone, Location


@pytest.fixture
def berlin(db_session):
    # |
    # |   *   *
    # |
    # | *
    # |     *
    # +------------
    shape = MultiPolygon([Polygon(((30, 10), (40, 40), (20, 40), (10, 20), (30, 10)))])

    tz = TimeZone(tzid="Europe/Berlin", the_geom=from_shape(shape, srid=4326))
    db_session.add(tz)
    db_session.commit()
    return tz


def test_repr(berlin):
    assert repr(berlin) == "<TimeZone: tzid='Europe/Berlin'>"
    assert isinstance(repr(berlin), str)


@pytest.mark.usefixtures("berlin")
def test_by_location_returns_timezone():
    tz = TimeZone.by_location(Location(longitude=20, latitude=30))
    assert tz is not None
    assert tz.zone == "Europe/Berlin"


@pytest.mark.usefixtures("berlin")
def test_by_location_returns_none_by_default():
    assert TimeZone.by_location(Location(longitude=10, latitude=10)) is None
