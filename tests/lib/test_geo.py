# -*- coding: utf-8 -*-

import pytest

from skylines.lib.geo import geographic_distance
from skylines.model.geo import Location


@pytest.mark.parametrize(
    "loc1,loc2,expected",
    [
        (
            Location(latitude=0.0, longitude=0.0),
            Location(latitude=0.0, longitude=0.0),
            0.0,
        ),
        (
            Location(latitude=38.898556, longitude=-77.037852),
            Location(latitude=38.897147, longitude=-77.043934),
            548.812,
        ),
    ],
)
def test_geographic_distance(loc1, loc2, expected):
    result = geographic_distance(loc1, loc2)
    assert result == pytest.approx(expected)
