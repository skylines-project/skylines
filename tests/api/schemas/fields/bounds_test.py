import pytest
from marshmallow import ValidationError

from skylines.api.schemas.fields.bounds import BoundsField


@pytest.fixture(scope='session')
def field():
    return BoundsField()


def test_deserialization(field):
    result = field.deserialize('-97.85,10.5,17,51.9')
    assert result.southwest.longitude == -97.85
    assert result.southwest.latitude == 10.5
    assert result.northeast.longitude == 17
    assert result.northeast.latitude == 51.9


def test_too_many_values(field):
    with pytest.raises(ValidationError):
        field.deserialize('1,2,3,4,5')


def test_not_enough_values(field):
    with pytest.raises(ValidationError):
        field.deserialize('1,2,3')
