from collections import OrderedDict

from skylines.api import schemas


def test_airport_schema(test_airport):
    """:type test_airport: skylines.model.Airport"""

    data, errors = schemas.airport_schema.dump(test_airport)
    assert not errors

    assert isinstance(data, OrderedDict)
    assert data.keys() == [
        'id',
        'name',
        'short_name',
        'icao',
        'country',
        'elevation',
        'location',
        'type',
        'runways',
        'frequencies',
        'created_at',
        'modified_at',
    ]

    assert data['id'] == test_airport.id
    assert data['name'] == test_airport.name
    assert data['short_name'] == test_airport.short_name
    assert data['icao'] == test_airport.icao
    assert data['country'] == test_airport.country_code
    assert data['elevation'] == test_airport.altitude
    assert data['type'] == test_airport.type

    location = data['location']
    assert isinstance(location, OrderedDict)
    assert location.keys() == ['longitude', 'latitude']
    assert location['longitude'] - test_airport.location.longitude < 0.00001
    assert location['latitude'] - test_airport.location.latitude < 0.00001

    runways = data['runways']
    assert isinstance(runways, list)
    runway = runways.pop()
    assert isinstance(runway, OrderedDict)
    assert runway.keys() == ['length', 'direction', 'surface']
    assert runway['length'] == test_airport.runway_len
    assert runway['direction'] == test_airport.runway_dir
    assert runway['surface'] == test_airport.surface

    frequencies = data['frequencies']
    assert isinstance(frequencies, list)
    frequency = frequencies.pop()
    assert isinstance(frequency, OrderedDict)
    assert frequency.keys() == ['frequency']
    assert frequency['frequency'] == test_airport.frequency


def test_airport_list_schema(test_airport):
    """:type test_airport: skylines.model.Airport"""

    data, errors = schemas.airport_list_schema.dump(test_airport)
    assert not errors

    assert isinstance(data, OrderedDict)
    assert data.keys() == [
        'id',
        'name',
        'elevation',
        'location',
    ]

    assert data['id'] == test_airport.id
    assert data['name'] == test_airport.name
    assert data['elevation'] == test_airport.altitude

    location = data['location']
    assert isinstance(location, OrderedDict)
    assert location.keys() == ['longitude', 'latitude']
    assert location['longitude'] - test_airport.location.longitude < 0.00001
    assert location['latitude'] - test_airport.location.latitude < 0.00001
