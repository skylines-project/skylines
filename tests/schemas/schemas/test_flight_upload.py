import pytest

from skylines.schemas import FlightUploadSchema


@pytest.fixture
def schema():
    return FlightUploadSchema(strict=False)


def test_empty_dict(schema):
    data, errors = schema.load({})
    assert data == None
    assert errors == {u"_schema": ["Either pilotName or pilotId must be set"]}


def test_pilot_id(schema):
    data, errors = schema.load({"pilotId": 123})
    assert data == {"pilot_id": 123}
    assert errors == {}


def test_pilot_id_as_string(schema):
    data, errors = schema.load({"pilotId": "123"})
    assert data == {"pilot_id": 123}
    assert errors == {}


def test_pilot_name(schema):
    data, errors = schema.load({"pilotName": "Johnny Dee"})
    assert data == {"pilot_name": "Johnny Dee"}
    assert errors == {}


def test_pilot_name_with_empty_id(schema):
    data, errors = schema.load({"pilotId": "", "pilotName": "Johnny Dee"})
    assert data == {"pilot_name": "Johnny Dee"}
    assert errors == {}


def test_invalid_pilot_id(schema):
    data, errors = schema.load({"pilotId": "foo"})
    assert data == {}
    assert errors == {"pilotId": [u"Not a valid integer."]}


def test_empty_pilot_name(schema):
    data, errors = schema.load({"pilotName": ""})
    assert data == None
    assert errors == {u"_schema": ["Either pilotName or pilotId must be set"]}


def test_pilot_id_and_name(schema):
    data, errors = schema.load({"pilotId": 123, "pilotName": "JD"})
    assert data == {"pilot_id": 123}
    assert errors == {}
