# coding=utf-8
from tests.data import add_fixtures, aircraft_models


def test_list_empty(db_session, client):
    res = client.get("/aircraft-models")
    assert res.status_code == 200
    assert res.json == {"models": []}


def test_list(db_session, client):
    nimeta = aircraft_models.nimeta()
    ask13 = aircraft_models.ask13()
    dimona = aircraft_models.dimona()
    epsilon = aircraft_models.epsilon()
    delta = aircraft_models.delta()
    falcon9 = aircraft_models.falcon9()
    add_fixtures(db_session, nimeta, ask13, dimona, epsilon, delta, falcon9)

    res = client.get("/aircraft-models")
    assert res.status_code == 200
    assert res.json == {
        "models": [
            {"id": ask13.id, "name": "ASK 13", "index": 17, "type": "unspecified"},
            {"id": nimeta.id, "index": 112, "name": "Nimeta", "type": "glider"},
            {"id": dimona.id, "index": None, "name": "Dimona", "type": "motorglider"},
            {"id": epsilon.id, "index": None, "name": "EPSILON", "type": "paraglider"},
            {"id": delta.id, "index": None, "name": u"Δ", "type": "hangglider"},
            {"id": falcon9.id, "index": None, "name": "Falcon 9", "type": "ul"},
        ]
    }
