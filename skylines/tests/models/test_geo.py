from nose.tools import eq_, assert_raises

from skylines.model import Bounds, Location


class TestBounds():
    def test_constructor(self):
        # Check that only Location instances are accepted
        assert_raises(ValueError, Bounds, 3, 5)

        sw = Location(latitude=49, longitude=6)
        ne = Location(latitude=51, longitude=7)
        b = Bounds(sw, ne)

        eq_(b.southwest.latitude, 49)
        eq_(b.southwest.longitude, 6)
        eq_(b.northeast.latitude, 51)
        eq_(b.northeast.longitude, 7)

    def test_from_bbox_string(self):
        # Check that strings with more or less than 4 components
        # raise ValueError
        assert_raises(ValueError, Bounds.from_bbox_string, '1,2,3')
        Bounds.from_bbox_string('1,2,3,4')
        assert_raises(ValueError, Bounds.from_bbox_string, '1,2,3,4,5')

        # Check that non-numeric values raise ValueError
        assert_raises(ValueError, Bounds.from_bbox_string, '1,a,3,4')

        # Check that BBox strings are parsed correctly
        b = Bounds.from_bbox_string('6.05,49.5,7,51.0')

        eq_(b.southwest.latitude, 49.5)
        eq_(b.southwest.longitude, 6.05)
        eq_(b.northeast.latitude, 51)
        eq_(b.northeast.longitude, 7)
