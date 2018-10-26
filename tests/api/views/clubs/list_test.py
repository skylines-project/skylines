from pytest_voluptuous import S
from voluptuous.validators import ExactSequence

from tests.data import add_fixtures, clubs


def test_list_all(db_session, client):
    add_fixtures(db_session, clubs.sfn(), clubs.lva())

    res = client.get("/clubs")
    assert res.status_code == 200
    assert res.json == S(
        {
            "clubs": ExactSequence(
                [
                    {"id": int, "name": "LV Aachen"},
                    {"id": int, "name": "Sportflug Niederberg"},
                ]
            )
        }
    )


def test_name_filter(db_session, client):
    add_fixtures(db_session, clubs.sfn(), clubs.lva())

    res = client.get("/clubs?name=LV%20Aachen")
    assert res.status_code == 200
    assert res.json == S({"clubs": ExactSequence([{"id": int, "name": "LV Aachen"}])})


def test_name_filter_with_unknown_club(db_session, client):
    res = client.get("/clubs?name=Unknown")
    assert res.status_code == 200
    assert res.json == S({"clubs": ExactSequence([])})
