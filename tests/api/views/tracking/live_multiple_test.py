from mock import patch
from datetime import datetime, timedelta

from tests.data import add_fixtures, users, live_fix
from tests.api.views.tracking import get_fixes_times_seconds, decode_time


def test_get_live_default_max_age(db_session, client):
    """The default max_age is 12 hours"""
    utcnow = datetime(year=2020, month=12, day=20, hour=20)

    john = users.john()
    john_fixes = []
    for age_hour in range(14, 0, -1):
        time = utcnow - timedelta(hours=age_hour)
        john_fixes.append(live_fix.create(john, time, 10, 20))

    jane = users.jane()
    jane_fixes = []
    for age_hour in range(14, 0, -1):
        time = utcnow - timedelta(hours=age_hour, minutes=30)
        jane_fixes.append(live_fix.create(jane, time, 11, 21))

    add_fixtures(db_session, john, *(john_fixes + jane_fixes))

    with patch("skylines.model.tracking.datetime") as datetime_mock:
        datetime_mock.utcnow.return_value = utcnow

        res = client.get("/live/{john},{jane}".format(john=john.id, jane=jane.id))

        assert res.status_code == 200
        json = res.json

        assert json == {
            u"flights": [
                {
                    u"additional": {u"color": u"#2b56d8", u"competition_id": u"JD"},
                    u"barogram_h": u"eE???????????",
                    u"barogram_t": u"_gw@_`F_`F_`F_`F_`F_`F_`F_`F_`F_`F_`F",
                    u"contests": None,
                    u"elevations_h": u"????????????",
                    u"elevations_t": u"_gw@_`F_`F_`F_`F_`F_`F_`F_`F_`F_`F_`F",
                    u"enl": u"",
                    u"geoid": 26.504,
                    u"points": u"_gayB_c`|@??????????????????????",
                    u"sfid": john.id,
                },
                {
                    u"additional": {u"color": u"#822bd8", u"competition_id": u"JD"},
                    u"barogram_h": u"eE??????????",
                    u"barogram_t": u"owz@_`F_`F_`F_`F_`F_`F_`F_`F_`F_`F",
                    u"contests": None,
                    u"elevations_h": u"???????????",
                    u"elevations_t": u"owz@_`F_`F_`F_`F_`F_`F_`F_`F_`F_`F",
                    u"enl": u"",
                    u"geoid": 25.013,
                    u"points": u"_qd_C_mcbA????????????????????",
                    u"sfid": jane.id,
                },
            ],
            u"pilots": [
                {
                    u"club": None,
                    u"color": u"#2b56d8",
                    u"firstName": u"John",
                    u"followers": 0,
                    u"following": 0,
                    u"id": john.id,
                    u"lastName": u"Doe",
                    u"name": u"John Doe",
                    u"trackingCallsign": None,
                    u"trackingDelay": 0,
                },
                {
                    u"club": None,
                    u"color": u"#822bd8",
                    u"firstName": u"Jane",
                    u"followers": 0,
                    u"following": 0,
                    u"id": jane.id,
                    u"lastName": u"Doe",
                    u"name": u"Jane Doe",
                    u"trackingCallsign": None,
                    u"trackingDelay": 0,
                },
            ],
        }

        expected_fixes = list(
            filter(lambda f: f.time >= utcnow - timedelta(hours=12), john_fixes)
        )
        assert decode_time(
            json[u"flights"][0][u"barogram_t"]
        ) == get_fixes_times_seconds(expected_fixes)

        expected_fixes = list(
            filter(lambda f: f.time >= utcnow - timedelta(hours=12), jane_fixes)
        )
        assert decode_time(
            json[u"flights"][1][u"barogram_t"]
        ) == get_fixes_times_seconds(expected_fixes)
