# coding=utf-8
from tests.data import add_fixtures, airports


def test_read_missing(db_session, client):
    res = client.get("/airports/1")
    assert res.status_code == 404
    assert res.json == {
        "message": "Sorry, there is no such record (1) in our database."
    }


def test_read(db_session, client):
    airport = airports.merzbrueck()
    add_fixtures(db_session, airport)

    res = client.get("/airports/{id}".format(id=airport.id))
    assert res.status_code == 200
    assert res.json == {
        "id": airport.id,
        "name": "Aachen Merzbruck",
        "elevation": 189.0,
        "short_name": None,
        "countryCode": "DE",
        "icao": "EDKA",
        "location": [6.186389, 50.823056],
    }
