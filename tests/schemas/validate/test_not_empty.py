from skylines.schemas import fields, validate, Schema


class TestSchema(Schema):
    name = fields.String(validate=validate.NotEmpty())


def test_fails_for_empty_string():
    data, errors = TestSchema().load(dict(name=''))
    assert 'name' in errors
    assert errors.get('name') == ['Must not be empty.']


def test_passes_for_non_empty_string():
    data, errors = TestSchema().load(dict(name='foobar'))
    assert not errors


def test_passes_for_blank_string():
    data, errors = TestSchema().load(dict(name='    '))
    assert not errors


def test_fails_for_stripped_blank_string():
    class TestSchema2(Schema):
        name = fields.String(strip=True, validate=validate.NotEmpty())

    data, errors = TestSchema2().load(dict(name='    '))
    assert 'name' in errors
    assert errors.get('name') == ['Must not be empty.']
