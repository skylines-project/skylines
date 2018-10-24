from skylines.schemas import fields, Schema
from skylines.model.geo import Location


def test_serialization():
    class TestSchema(Schema):
        location = fields.Location()

    data = TestSchema().dump(dict(location=Location(longitude=7, latitude=51))).data
    assert data["location"] == [7, 51]
