from collections import OrderedDict

from skylines.api import schemas


def test_airspace_list_schema(test_airspace):
    """:type test_airspace: skylines.model.Airspace"""

    data, errors = schemas.airspace_list_schema.dump(test_airspace)
    assert not errors

    assert isinstance(data, OrderedDict)
    assert data.keys() == [
        'name',
        'class',
        'top',
        'base',
        'country',
    ]

    assert data['name'] == test_airspace.name
    assert data['class'] == test_airspace.airspace_class
    assert data['top'] == test_airspace.top
    assert data['base'] == test_airspace.base
    assert data['country'] == test_airspace.country_code
