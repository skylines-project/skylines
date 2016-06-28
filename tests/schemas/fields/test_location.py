from skylines.schemas import fields, Schema
from skylines.model.geo import Location


def test_serialization():
    class TestSchema(Schema):
        location = fields.Location()

    data, errors = TestSchema().dump(dict(location=Location(longitude=7, latitude=51)))
    assert not errors
    assert data.get('location') == [7, 51]
