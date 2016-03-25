from collections import OrderedDict, namedtuple

from skylines.api import schemas

Wave = namedtuple('Wave', ('name', 'main_wind_direction'))


def test_wave_list_schema():
    data, errors = schemas.wave_list_schema.dump(Wave(u'Test Wave #1', u'123'))
    assert not errors

    assert isinstance(data, OrderedDict)
    assert data.keys() == [
        'name',
        'main_wind_direction',
    ]

    assert data['name'] == u'Test Wave #1'
    assert data['main_wind_direction'] == u'123\u00B0'
