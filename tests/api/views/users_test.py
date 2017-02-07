def test_list_users(client, test_users):
    res = client.get('/users/')
    assert res.status_code == 200

    users = res.json['users']
    assert len(users) > 0

    first_user = users[0]
    assert 'id' in first_user
    assert 'name' in first_user


def test_read_user(client, test_user):
    res = client.get('/users/{}'.format(test_user.id))
    assert res.status_code == 200

    json = res.json
    assert json['id'] == test_user.id
    assert json['name'] == test_user.name
    assert json['trackingCallsign'] is None


def test_read_missing_user(client):
    res = client.get('/users/1000000000000')
    assert res.status_code == 404


def test_read_user_with_invalid_id(client):
    res = client.get('/users/abc')
    assert res.status_code == 404
