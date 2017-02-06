# coding=utf-8
from skylines.model import AircraftModel
from tests.data import add_fixtures


def test_list_empty(db_session, client):
    res = client.get('/aircraft-models')
    assert res.status_code == 200
    assert res.json == {
        'models': [],
    }


def test_list(db_session, client):
    models = [
        AircraftModel(name='Nimeta', kind=1, igc_index=142, dmst_index=100),
        AircraftModel(name='ASK 13', igc_index=42, dmst_index=17),
        AircraftModel(name='Dimona', kind=2),
        AircraftModel(name='EPSILON', kind=3),
        AircraftModel(name=u'Δ', kind=4),
        AircraftModel(name='Falcon 9', kind=5),
    ]
    add_fixtures(db_session, *models)

    res = client.get('/aircraft-models')
    print res.json
    assert res.status_code == 200
    assert res.json == {
        'models': [{
            'id': models[1].id,
            'name': 'ASK 13',
            'index': 17,
            'type': 'unspecified',
        }, {
            'id': models[0].id,
            'index': 100,
            'name': 'Nimeta',
            'type': 'glider'
        }, {
            'id': models[2].id,
            'index': None,
            'name': 'Dimona',
            'type': 'motorglider'
        }, {
            'id': models[3].id,
            'index': None,
            'name': 'EPSILON',
            'type': 'paraglider'
        }, {
            'id': models[4].id,
            'index': None,
            'name': u'Δ',
            'type': 'hangglider'
        }, {
            'id': models[5].id,
            'index': None,
            'name': 'Falcon 9',
            'type': 'ul'
        }]
    }
