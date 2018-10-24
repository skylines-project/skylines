from skylines.schemas import fields, Schema


def test_default_deserialization():
    class TestSchema(Schema):
        name = fields.String()

    data, errors = TestSchema().load(dict(name="   foo bar   "))
    assert not errors
    assert data.get("name") == "   foo bar   "


def test_stripping_deserialization():
    class TestSchema(Schema):
        name = fields.String(strip=True)

    data, errors = TestSchema().load(dict(name="   foo bar   "))
    assert not errors
    assert data.get("name") == "foo bar"


def test_abbr_deserialization():
    class TestSchema(Schema):
        name = fields.Str(strip=True)

    data, errors = TestSchema().load(dict(name="   foo bar   "))
    assert not errors
    assert data.get("name") == "foo bar"
