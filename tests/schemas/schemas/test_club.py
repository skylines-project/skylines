from skylines.schemas import ClubSchema


def test_deserialization_fails_for_empty_name():
    data, errors = ClubSchema(only=('name',)).load(dict(name=''))
    assert 'name' in errors
    assert 'Must not be empty.' in errors.get('name')


def test_deserialization_fails_for_spaced_name():
    data, errors = ClubSchema(only=('name',)).load(dict(name='      '))
    assert 'name' in errors
    assert 'Must not be empty.' in errors.get('name')


def test_deserialization_passes_for_valid_name():
    data, errors = ClubSchema(only=('name',)).load(dict(name=' foo  '))
    assert not errors
    assert data.get('name') == 'foo'
