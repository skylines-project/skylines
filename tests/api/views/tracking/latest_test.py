from mock import patch
from datetime import datetime, timedelta
from tests.data import add_fixtures, users, live_fix


def test_get_latest_default_max_age(db_session, client):
    """The default max_age is 6 hours"""
    utcnow = datetime(year=2020, month=12, day=20, hour=12)

    # Only the latest_fix should be returned
    john = users.john()
    fix = live_fix.create(john, utcnow - timedelta(hours=2), 10, 20)
    latest_fix = live_fix.create(john, utcnow - timedelta(minutes=5), 11, 21)

    # Fix older than 6h should not be returned
    jane = users.jane()
    old_fix = live_fix.create(jane, utcnow - timedelta(hours=7), 12, 22)

    add_fixtures(db_session, john, fix, latest_fix, jane, old_fix)

    with patch("skylines.model.tracking.datetime") as datetime_mock:
        datetime_mock.utcnow.return_value = utcnow

        res = client.get("/tracking/latest.json")

        assert res.status_code == 200
        assert res.json == {
            u"fixes": [
                {
                    u"airspeed": 10,
                    u"altitude": 100,
                    u"ground_speed": 10,
                    u"location": u"POINT(11.0 21.0)",
                    u"pilot": {u"id": john.id, u"name": u"John Doe"},
                    u"time": u"2020-12-20T11:55:00Z",
                    u"track": 0,
                    u"vario": 0,
                }
            ]
        }
