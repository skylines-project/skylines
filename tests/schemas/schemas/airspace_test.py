from collections import OrderedDict
from datetime import datetime

from geoalchemy2.shape import to_shape
from shapely.geometry import Polygon

from skylines.schemas import AirspaceSchema


def test_airspace_schema(test_airspace):
    """:type test_airspace: skylines.model.Airspace"""

    data, errors = AirspaceSchema().dump(test_airspace)
    assert not errors

    assert isinstance(data, OrderedDict)
    assert list(data.keys()) == [
        "id",
        "name",
        "class",
        "base",
        "top",
        "shape",
        "countryCode",
        "created_at",
        "modified_at",
    ]

    assert data["id"] == test_airspace.id
    assert data["name"] == test_airspace.name
    assert data["class"] == test_airspace.airspace_class
    assert data["top"] == test_airspace.top
    assert data["base"] == test_airspace.base
    assert data["countryCode"] == test_airspace.country_code

    created_at = datetime.strptime(data["created_at"], "%Y-%m-%dT%H:%M:%S.%f+00:00")
    assert isinstance(created_at, datetime)
    assert created_at == test_airspace.time_created

    modified_at = datetime.strptime(data["modified_at"], "%Y-%m-%dT%H:%M:%S.%f+00:00")
    assert isinstance(modified_at, datetime)
    assert modified_at == test_airspace.time_modified

    test_shape = to_shape(test_airspace.the_geom)
    assert isinstance(test_shape, Polygon)

    shape = data["shape"]
    assert isinstance(shape, list)
    assert len(shape) == len(test_shape.exterior.coords)

    c2 = shape[1]
    test_c2 = test_shape.exterior.coords[1]

    assert c2[0] == test_c2[0]
    assert c2[1] == test_c2[1]
