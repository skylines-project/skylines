from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon

from skylines.model import Airspace


def test_airspace():
    shape = Polygon(((30, 10), (40, 40), (20, 40), (10, 20), (30, 10)))

    return Airspace(
        name='TestAirspace',
        airspace_class='WAVE',
        top='FL100',
        base='4500ft',
        country_code='de',
        the_geom=from_shape(shape, srid=4326),
    )
