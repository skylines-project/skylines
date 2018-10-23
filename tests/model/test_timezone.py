# -*- coding: utf-8 -*-
import pytest

from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon, MultiPolygon

from skylines.model import TimeZone


@pytest.fixture
def berlin(db_session):
    shape = MultiPolygon([Polygon(((30, 10), (40, 40), (20, 40), (10, 20), (30, 10)))])

    tz = TimeZone(tzid='Europe/Berlin', the_geom=from_shape(shape, srid=4326))
    db_session.add(tz)
    db_session.commit()
    return tz


def test_repr(berlin):
    assert repr(berlin) == '<TimeZone: tzid=\'Europe/Berlin\'>'
    assert isinstance(repr(berlin), str)
