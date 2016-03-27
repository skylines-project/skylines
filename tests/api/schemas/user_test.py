from collections import OrderedDict
from datetime import datetime

from skylines.api import schemas


def test_user_schema(test_user):
    """:type test_user: skylines.model.User"""

    data, errors = schemas.user_schema.dump(test_user)
    assert not errors

    assert isinstance(data, OrderedDict)
    assert data.keys() == [
        'id',
        'name',
        'first_name',
        'last_name',
        'club',
        'tracking_delay',
        'tracking_call_sign',
        'created_at'
    ]

    assert data['id'] == test_user.id
    assert data['name'] == test_user.name
    assert data['first_name'] == test_user.first_name
    assert data['last_name'] == test_user.last_name
    assert data['tracking_delay'] == test_user.tracking_delay
    assert data['tracking_call_sign'] == test_user.tracking_callsign

    created_at = datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%S.%f+00:00')
    assert isinstance(created_at, datetime)
    assert created_at == test_user.created


def test_user_list_schema(test_user):
    """:type test_user: skylines.model.User"""

    data, errors = schemas.user_list_schema.dump(test_user)
    assert not errors

    assert isinstance(data, OrderedDict)
    assert data.keys() == [
        'id',
        'name',
        'first_name',
        'last_name',
    ]

    assert data['id'] == test_user.id
    assert data['name'] == test_user.name
    assert data['first_name'] == test_user.first_name
    assert data['last_name'] == test_user.last_name


def test_current_user_schema(test_user):
    """:type test_user: skylines.model.User"""

    data, errors = schemas.current_user_schema.dump(test_user)
    assert not errors

    assert isinstance(data, OrderedDict)
    assert data.keys() == [
        'id',
        'name',
        'first_name',
        'last_name',
        'club',
        'tracking_delay',
        'tracking_call_sign',
        'created_at',
        'email',
        'tracking_key',
        'admin',
    ]

    assert data['id'] == test_user.id
    assert data['name'] == test_user.name
    assert data['first_name'] == test_user.first_name
    assert data['last_name'] == test_user.last_name
    assert data['email'] == test_user.email_address
    assert data['tracking_key'] == ('%X' % test_user.tracking_key)
    assert data['tracking_delay'] == test_user.tracking_delay
    assert data['tracking_call_sign'] == test_user.tracking_callsign

    created_at = datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%S.%f+00:00')
    assert isinstance(created_at, datetime)
    assert created_at == test_user.created
