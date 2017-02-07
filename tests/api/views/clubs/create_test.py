from skylines.model import Club
from tests.api import basic_auth


def test_create(db_session, client, test_user):
    headers = basic_auth(test_user.email_address, test_user.original_password)

    res = client.put('/clubs', headers=headers, json={
        'name': 'LV Aachen',
    })
    assert res.status_code == 200
    assert Club.get(res.json['id'])
