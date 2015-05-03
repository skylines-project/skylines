import pytest
from skylines.model import Bounds, Location


def test_constructor():
    # Check that only Location instances are accepted
    with pytest.raises(ValueError): Bounds(3, 5)

    sw = Location(latitude=49, longitude=6)
    ne = Location(latitude=51, longitude=7)
    b = Bounds(sw, ne)

    assert b.southwest.latitude == 49
    assert b.southwest.longitude == 6
    assert b.northeast.latitude == 51
    assert b.northeast.longitude == 7


def test_from_bbox_string():
    # Check that strings with more or less than 4 components
    # raise ValueError
    with pytest.raises(ValueError): Bounds.from_bbox_string('1,2,3')
    Bounds.from_bbox_string('1,2,3,4')
    with pytest.raises(ValueError): Bounds.from_bbox_string('1,2,3,4,5')

    # Check that non-numeric values raise ValueError
    with pytest.raises(ValueError): Bounds.from_bbox_string('1,a,3,4')

    # Check that BBox strings are parsed correctly
    b = Bounds.from_bbox_string('6.05,49.5,7,51.0')

    assert b.southwest.latitude == 49.5
    assert b.southwest.longitude == 6.05
    assert b.northeast.latitude == 51
    assert b.northeast.longitude == 7


def test_get_sizes():
    # Check normal size calculations
    b = Bounds.from_bbox_string('1,50,21,52')

    assert b.get_width() == 20
    assert b.get_height() == 2
    assert b.get_size() == 40

    # Check longitude wraparound and height == 0
    b = Bounds.from_bbox_string('170,50,-165,50')

    assert b.get_width() == 25
    assert b.get_height() == 0
    assert b.get_size() == 0
