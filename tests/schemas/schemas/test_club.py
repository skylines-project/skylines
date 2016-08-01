import pytest

from marshmallow import ValidationError

from skylines.schemas import ClubSchema


def test_deserialization_fails_for_empty_name():
    with pytest.raises(ValidationError) as e:
        ClubSchema(only=('name',)).load(dict(name=''))

    errors = e.value.messages
    assert 'name' in errors
    assert 'Must not be empty.' in errors.get('name')


def test_deserialization_fails_for_spaced_name():
    with pytest.raises(ValidationError) as e:
        ClubSchema(only=('name',)).load(dict(name='      '))

    errors = e.value.messages
    assert 'name' in errors
    assert 'Must not be empty.' in errors.get('name')


def test_deserialization_passes_for_valid_name():
    data = ClubSchema(only=('name',)).load(dict(name=' foo  ')).data

    assert data['name'] == 'foo'


def test_serialization_passes_for_invalid_website():
    data = ClubSchema().dump(dict(website='foobar')).data
    assert data['website'] == 'foobar'
