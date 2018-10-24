import pytest

from marshmallow import ValidationError

from skylines.schemas import ClubSchema


def test_deserialization_fails_for_empty_name():
    with pytest.raises(ValidationError) as e:
        ClubSchema(only=("name",)).load(dict(name=""))

    errors = e.value.messages
    assert "name" in errors
    assert "Must not be empty." in errors.get("name")


def test_deserialization_fails_for_spaced_name():
    with pytest.raises(ValidationError) as e:
        ClubSchema(only=("name",)).load(dict(name="      "))

    errors = e.value.messages
    assert "name" in errors
    assert "Must not be empty." in errors.get("name")


def test_deserialization_passes_for_valid_name():
    data = ClubSchema(only=("name",)).load(dict(name=" foo  ")).data

    assert data["name"] == "foo"


def test_deserialization_passes_for_valid_website():
    data = ClubSchema(partial=True).load(dict(website="https://skylines.aero")).data

    assert data["website"] == "https://skylines.aero"


def test_deserialization_passes_for_empty_website():
    data = ClubSchema(partial=True).load(dict(website="")).data

    assert data["website"] == ""


def test_deserialization_passes_for_null_website():
    data = ClubSchema(partial=True).load(dict(website=None)).data

    assert data["website"] is None


def test_deserialization_fails_for_invalid_website():
    with pytest.raises(ValidationError) as e:
        ClubSchema(partial=True).load(dict(website="foo"))

    errors = e.value.messages
    assert "website" in errors
    assert "Not a valid URL." in errors.get("website")


def test_serialization_passes_for_invalid_website():
    data = ClubSchema().dump(dict(website="foobar")).data
    assert data["website"] == "foobar"
