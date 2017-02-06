from tests.data import add_fixtures, clubs


def test_list_all(db_session, client):
    sfn = clubs.sfn()
    lva = clubs.lva()
    add_fixtures(db_session, sfn, lva)

    res = client.get('/clubs')
    assert res.status_code == 200
    assert res.json == {
        'clubs': [{
            'id': lva.id,
            'name': 'LV Aachen',
        }, {
            'id': sfn.id,
            'name': 'Sportflug Niederberg',
        }]
    }


def test_name_filter(db_session, client):
    sfn = clubs.sfn()
    lva = clubs.lva()
    add_fixtures(db_session, sfn, lva)

    res = client.get('/clubs?name=LV%20Aachen')
    assert res.status_code == 200
    assert res.json == {
        'clubs': [{
            'id': lva.id,
            'name': 'LV Aachen',
        }]
    }


def test_name_filter_with_unknown_club(db_session, client):
    res = client.get('/clubs?name=Unknown')
    assert res.status_code == 200
    assert res.json == {
        'clubs': []
    }
