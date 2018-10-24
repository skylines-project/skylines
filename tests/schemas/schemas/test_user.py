import pytest

from marshmallow import ValidationError

from skylines.schemas import UserSchema


@pytest.fixture
def schema():
    return UserSchema()


@pytest.fixture
def partial_schema():
    return UserSchema(partial=True)


@pytest.fixture
def callsign_schema():
    return UserSchema(only=("trackingCallsign",))


@pytest.fixture
def delay_schema():
    return UserSchema(only=("trackingDelay",))


def test_deserialization_skips_id(partial_schema):
    data = partial_schema.load(dict(id=6)).data
    assert "id" not in data


def test_deserialization_passes_for_valid_callsign(callsign_schema):
    data = callsign_schema.load(dict(trackingCallsign="TH")).data
    assert data["tracking_callsign"] == "TH"


def test_deserialization_passes_for_missing_callsign(callsign_schema):
    data = callsign_schema.load(dict()).data
    assert "tracking_callsign" not in data


def test_deserialization_passes_for_empty_callsign(callsign_schema):
    data = callsign_schema.load(dict(trackingCallsign="")).data
    assert data["tracking_callsign"] == ""


def test_deserialization_passes_for_stripped_callsign(callsign_schema):
    data = callsign_schema.load(dict(trackingCallsign="TH           ")).data
    assert data["tracking_callsign"] == "TH"


def test_deserialization_fails_for_long_callsign(callsign_schema):
    with pytest.raises(ValidationError) as e:
        callsign_schema.load(dict(trackingCallsign="12345890"))

    errors = e.value.messages
    assert "trackingCallsign" in errors
    assert "Longer than maximum length 5." in errors["trackingCallsign"]


def test_deserialization_passes_for_valid_delay(delay_schema):
    data = delay_schema.load(dict(trackingDelay=5)).data
    assert data["tracking_delay"] == 5


def test_deserialization_passes_for_valid_delay_string(delay_schema):
    data = delay_schema.load(dict(trackingDelay="10")).data
    assert data["tracking_delay"] == 10


def test_deserialization_fails_for_invalid_delay(delay_schema):
    with pytest.raises(ValidationError) as e:
        delay_schema.load(dict(trackingDelay=-1))

    errors = e.value.messages
    assert "trackingDelay" in errors
    assert "Must be between 0 and 60." in errors["trackingDelay"]
