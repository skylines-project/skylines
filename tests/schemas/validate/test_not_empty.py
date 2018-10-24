import pytest

from marshmallow import ValidationError

from skylines.schemas import fields, validate, Schema


class ExampleSchema(Schema):
    name = fields.String(validate=validate.NotEmpty())


def test_fails_for_empty_string():
    with pytest.raises(ValidationError) as e:
        ExampleSchema().load(dict(name=""))

    errors = e.value.messages
    assert "name" in errors
    assert "Must not be empty." in errors["name"]


def test_passes_for_non_empty_string():
    data = ExampleSchema().load(dict(name="foobar")).data
    assert data["name"] == "foobar"


def test_passes_for_blank_string():
    data = ExampleSchema().load(dict(name="    ")).data
    assert data["name"] == "    "


def test_fails_for_stripped_blank_string():
    class TestSchema2(Schema):
        name = fields.String(strip=True, validate=validate.NotEmpty())

    with pytest.raises(ValidationError) as e:
        TestSchema2().load(dict(name="    "))

    errors = e.value.messages
    assert "name" in errors
    assert "Must not be empty." in errors["name"]
