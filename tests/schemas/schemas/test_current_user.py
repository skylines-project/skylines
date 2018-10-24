import pytest

from marshmallow import ValidationError

from skylines.schemas import CurrentUserSchema


@pytest.fixture
def schema():
    return CurrentUserSchema()


@pytest.fixture
def partial_schema():
    return CurrentUserSchema(partial=True)


def test_serialization_passes_for_invalid_email(schema):
    data = schema.dump(dict(email_address="foobar")).data
    assert data["email"] == "foobar"


def test_deserialization_passes_for_valid_email(partial_schema):
    data = partial_schema.load(dict(email="john@doe.com")).data
    assert data["email_address"] == "john@doe.com"


def test_deserialization_fails_for_empty_email(partial_schema):
    with pytest.raises(ValidationError) as e:
        partial_schema.load(dict(email=""))

    errors = e.value.messages
    assert "email" in errors
    assert "Not a valid email address." in errors["email"]
