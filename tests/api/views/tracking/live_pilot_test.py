from mock import patch
from datetime import datetime, timedelta

from tests.data import add_fixtures, users, live_fix
from tests.api.views.tracking import get_fixes_times_seconds, decode_time, to_timestamp


def test_get_live_default_max_age(db_session, client):
    """The default max_age is 12 hours"""
    utcnow = datetime(year=2020, month=12, day=20, hour=20)

    john = users.john()
    fixes = []
    for age_hour in range(14, 0, -1):
        time = utcnow - timedelta(hours=age_hour)
        fixes.append(live_fix.create(john, time, 10, 20))

    add_fixtures(db_session, john, *fixes)

    with patch("skylines.model.tracking.datetime") as datetime_mock:
        datetime_mock.utcfromtimestamp.side_effect = lambda *args, **kw: datetime.utcfromtimestamp(
            *args, **kw
        )
        datetime_mock.utcnow.return_value = utcnow

        res = client.get("/live/{id}/json".format(id=john.id))

        assert res.status_code == 200
        json = res.json

        assert json == {
            u"barogram_h": u"eE???????????",
            u"barogram_t": u"_gw@_`F_`F_`F_`F_`F_`F_`F_`F_`F_`F_`F",
            u"elevations": u"????????????",
            u"enl": u"",
            u"geoid": 26.504,
            u"points": u"_gayB_c`|@??????????????????????",
            u"sfid": john.id,
        }

        expected_fixes = list(
            filter(lambda f: f.time >= utcnow - timedelta(hours=12), fixes)
        )
        assert decode_time(json[u"barogram_t"]) == get_fixes_times_seconds(
            expected_fixes
        )


def test_get_live_filter_by_last_update(db_session, client):
    utcnow = datetime(year=2020, month=12, day=20, hour=20)
    last_update = 50000
    start_time = datetime(year=2020, month=12, day=20) + timedelta(seconds=last_update)

    john = users.john()
    fixes = []
    for age_hour in range(14, 0, -1):
        time = utcnow - timedelta(hours=age_hour)
        fixes.append(live_fix.create(john, time, 10, 20))

    add_fixtures(db_session, john, *fixes)

    with patch("skylines.model.tracking.datetime") as datetime_mock:
        datetime_mock.utcfromtimestamp.side_effect = lambda *args, **kw: datetime.utcfromtimestamp(
            *args, **kw
        )
        datetime_mock.utcnow.return_value = utcnow

        res = client.get(
            "/live/{id}/json?last_update={last_update}".format(
                id=john.id, last_update=last_update
            )
        )

        assert res.status_code == 200
        json = res.json

        print(decode_time(json[u"barogram_t"]))
        print(get_fixes_times_seconds(fixes))

        assert json == {
            u"barogram_h": u"eE?????",
            u"barogram_t": u"_maB_`F_`F_`F_`F_`F",
            u"elevations": u"??????",
            u"enl": u"",
            u"geoid": 26.504,
            u"points": u"_gayB_c`|@??????????",
            u"sfid": john.id,
        }

        expected_fixes = list(filter(lambda f: f.time >= start_time, fixes))
        assert decode_time(json[u"barogram_t"]) == get_fixes_times_seconds(
            expected_fixes
        )


def test_get_live_filter_by_from_time(db_session, client):
    utcnow = datetime(year=2020, month=12, day=20, hour=20)
    from_time = datetime(year=2020, month=12, day=20) + timedelta(seconds=50000)

    john = users.john()
    fixes = []
    for age_hour in range(14, 0, -1):
        time = utcnow - timedelta(hours=age_hour)
        fixes.append(live_fix.create(john, time, 10, 20))

    add_fixtures(db_session, john, *fixes)

    with patch("skylines.model.tracking.datetime") as datetime_mock:
        datetime_mock.utcfromtimestamp.side_effect = lambda *args, **kw: datetime.utcfromtimestamp(
            *args, **kw
        )
        datetime_mock.utcnow.return_value = utcnow

        res = client.get(
            "/live/{id}/json?from_time={from_time}".format(
                id=john.id, from_time=to_timestamp(from_time)
            )
        )

        assert res.status_code == 200
        json = res.json

        assert json == {
            u"barogram_h": u"eE?????",
            u"barogram_t": u"_maB_`F_`F_`F_`F_`F",
            u"elevations": u"??????",
            u"enl": u"",
            u"geoid": 26.504,
            u"points": u"_gayB_c`|@??????????",
            u"sfid": john.id,
        }

        expected_fixes = list(filter(lambda f: f.time >= from_time, fixes))
        assert decode_time(json[u"barogram_t"]) == get_fixes_times_seconds(
            expected_fixes
        )

        # Test that max age = 12h
        res = client.get("/live/{id}/json?from_time=0".format(id=john.id))

        assert res.status_code == 200
        json = res.json

        assert json == {
            u"barogram_h": u"eE???????????",
            u"barogram_t": u"_gw@_`F_`F_`F_`F_`F_`F_`F_`F_`F_`F_`F",
            u"elevations": u"????????????",
            u"enl": u"",
            u"geoid": 26.504,
            u"points": u"_gayB_c`|@??????????????????????",
            u"sfid": john.id,
        }

        expected_fixes = list(
            filter(lambda f: f.time >= utcnow - timedelta(hours=12), fixes)
        )
        assert decode_time(json[u"barogram_t"]) == get_fixes_times_seconds(
            expected_fixes
        )


def test_get_live_filter_by_last_update_and_from_time(db_session, client):
    utcnow = datetime(year=2020, month=12, day=20, hour=20)
    last_update = 50000
    start_time = datetime(year=2020, month=12, day=20) + timedelta(seconds=last_update)
    from_time = datetime(year=2020, month=12, day=20) + timedelta(seconds=40000)

    john = users.john()
    fixes = []
    for age_hour in range(14, 0, -1):
        time = utcnow - timedelta(hours=age_hour)
        fixes.append(live_fix.create(john, time, 10, 20))

    add_fixtures(db_session, john, *fixes)

    with patch("skylines.model.tracking.datetime") as datetime_mock:
        datetime_mock.utcfromtimestamp.side_effect = lambda *args, **kw: datetime.utcfromtimestamp(
            *args, **kw
        )
        datetime_mock.utcnow.return_value = utcnow

        # from_time is earlier than last_update
        res = client.get(
            "/live/{id}/json?last_update={last_update}&from_time={from_time}".format(
                id=john.id, last_update=last_update, from_time=to_timestamp(from_time)
            )
        )

        assert res.status_code == 200
        json = res.json

        print(decode_time(json[u"barogram_t"]))
        print(get_fixes_times_seconds(fixes))

        assert json == {
            u"barogram_h": u"eE?????",
            u"barogram_t": u"_maB_`F_`F_`F_`F_`F",
            u"elevations": u"??????",
            u"enl": u"",
            u"geoid": 26.504,
            u"points": u"_gayB_c`|@??????????",
            u"sfid": john.id,
        }

        expected_fixes = list(filter(lambda f: f.time >= start_time, fixes))
        assert decode_time(json[u"barogram_t"]) == get_fixes_times_seconds(
            expected_fixes
        )

    last_update = 40000
    start_time = datetime(year=2020, month=12, day=20) + timedelta(seconds=last_update)
    from_time = datetime(year=2020, month=12, day=20) + timedelta(seconds=50000)

    # last_update is earlier than from_time
    with patch("skylines.model.tracking.datetime") as datetime_mock:
        datetime_mock.utcfromtimestamp.side_effect = lambda *args, **kw: datetime.utcfromtimestamp(
            *args, **kw
        )
        datetime_mock.utcnow.return_value = utcnow

        res = client.get(
            "/live/{id}/json?last_update={last_update}&from_time={from_time}".format(
                id=john.id, last_update=last_update, from_time=to_timestamp(from_time)
            )
        )

        assert res.status_code == 200
        json = res.json

        print(decode_time(json[u"barogram_t"]))
        print(get_fixes_times_seconds(fixes))

        assert json == {
            u"barogram_h": u"eE?????",
            u"barogram_t": u"_maB_`F_`F_`F_`F_`F",
            u"elevations": u"??????",
            u"enl": u"",
            u"geoid": 26.504,
            u"points": u"_gayB_c`|@??????????",
            u"sfid": john.id,
        }

        expected_fixes = list(filter(lambda f: f.time >= from_time, fixes))
        assert decode_time(json[u"barogram_t"]) == get_fixes_times_seconds(
            expected_fixes
        )
