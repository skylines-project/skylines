# coding=utf-8
from tests.data import add_fixtures, users, clubs, airports


def test_search(db_session, client):
    edka = airports.merzbrueck()
    lva = clubs.lva()

    add_fixtures(
        db_session,
        users.john(),
        users.jane(),
        lva,
        clubs.sfn(),
        edka,
        airports.meiersberg(),
    )

    res = client.get("/search?text=aachen")
    assert res.status_code == 200
    assert res.json == {
        "results": [
            {
                "id": edka.id,
                "type": "airport",
                "name": "Aachen Merzbruck",
                "icao": "EDKA",
                "frequency": "122.875",
            },
            {
                "id": lva.id,
                "type": "club",
                "name": "LV Aachen",
                "website": "http://www.lv-aachen.de",
            },
        ]
    }


def test_search_doe(db_session, client):
    john = users.john()
    jane = users.jane()

    add_fixtures(
        db_session,
        john,
        jane,
        clubs.lva(),
        clubs.sfn(),
        airports.merzbrueck(),
        airports.meiersberg(),
    )

    res = client.get("/search?text=doe")
    assert res.status_code == 200
    assert res.json == {
        "results": [
            {"id": jane.id, "type": "user", "name": "Jane Doe"},
            {"id": john.id, "type": "user", "name": "John Doe"},
        ]
    }


def test_search_with_umlauts(db_session, client):
    john = users.john(last_name=u"Müller")

    add_fixtures(db_session, john)

    res = client.get(u"/search?text=M%C3%BCll")
    assert res.status_code == 200
    assert res.json == {
        "results": [{"id": john.id, "type": "user", "name": u"John Müller"}]
    }


def test_missing_search_text(client):
    res = client.get("/search")
    assert res.status_code == 200
    assert res.json == {"results": []}
