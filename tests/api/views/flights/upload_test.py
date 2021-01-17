from mock import patch
from pytest_voluptuous import S, Partial
from voluptuous.validators import ExactSequence, Datetime, Match, IsTrue
from werkzeug.datastructures import MultiDict

from skylines.lib.compat import text_type
from skylines.worker import tasks

from tests.api import auth_for
from tests.data import users, igcs


def test_upload(db_session, client):
    john = users.john()
    db_session.add(john)
    db_session.commit()

    data = dict(
        pilotId=john.id,
        pilotName="test",
        files=(igcs.simple_path,),
    )

    res = client.post("/flights/upload", headers=auth_for(john), data=data)
    assert res.status_code == 200
    assert res.json == S(
        {
            u"club_members": list,
            u"aircraft_models": list,
            u"results": ExactSequence(
                [
                    {
                        u"status": 0,
                        u"cacheKey": IsTrue(),
                        u"flight": {
                            u"pilotName": None,
                            u"takeoffAirport": None,
                            u"registration": u"LY-KDR",
                            u"speed": 30.63035019455253,
                            u"id": int,
                            u"privacyLevel": 2,
                            u"takeoffTime": u"2011-06-18T09:11:23+00:00",
                            u"score": 9.073321994774085,
                            u"scoreEndTime": u"2011-06-18T09:15:40+00:00",
                            u"copilot": None,
                            u"timeCreated": Datetime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
                            u"scoreStartTime": u"2011-06-18T09:11:23+00:00",
                            u"club": None,
                            u"scoreDate": u"2011-06-18T09:11:23",
                            u"landingTime": u"2011-06-18T09:15:40+00:00",
                            u"rawScore": 9.073321994774085,
                            u"copilotName": None,
                            u"pilot": {
                                u"id": john.id,
                                u"name": john.name,
                            },
                            u"distance": 7872,
                            u"igcFile": {
                                u"date": u"2011-06-18",
                                u"model": u"ASK13",
                                u"registration": u"LY-KDR",
                                u"competitionId": None,
                                u"filename": Match(r"simple(_\d+)?.igc"),
                                u"weglideStatus": None,
                                u"weglideData": None,
                            },
                            u"landingAirport": None,
                            u"triangleDistance": 4003,
                            u"model": None,
                            u"competitionId": None,
                        },
                        u"name": Match(r".*simple.igc"),
                        u"trace": {
                            u"barogram_h": u"yG?K@?????????????????????????????????????D?????EEEEIEKOIMSMIKOUWKOOOGUIEg@c@SUEKIKEEKI[]_@a@WSGYQk@",
                            u"igc_end_time": u"2011-06-18T09:15:40+00:00",
                            u"enl": u"??????????????????????????????????????????????????????????????????????????????????????????????",
                            u"elevations_h": u"n}@?????????????????????????????????????????????????????????????????????????????????????????????",
                            u"igc_start_time": u"2011-06-18T09:07:49+00:00",
                            u"barogram_t": u"ie_AIIIIIIIIIIIIIIKIIIIKIKIIIIIIIIIIIIIIIKIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIMIIIIIIIIIIIIIIIIIIIIII",
                        },
                        u"airspaces": ExactSequence([]),
                    }
                ]
            ),
        }
    )


def test_upload_zips(db_session, client):
    john = users.john()
    db_session.add(john)
    db_session.commit()

    data = dict(
        pilotId="",
        pilotName="Johnny Dee",
        files=(igcs.zip_path,),
    )

    res = client.post("/flights/upload", headers=auth_for(john), data=data)
    assert res.status_code == 200
    assert res.json == S(
        {
            u"club_members": list,
            u"aircraft_models": list,
            u"results": ExactSequence(
                [
                    {
                        u"status": 0,
                        u"cacheKey": text_type,
                        u"flight": Partial(
                            {
                                u"club": None,
                                u"copilot": None,
                                u"copilotName": None,
                                u"distance": 171246,
                                u"igcFile": dict,
                                u"pilot": None,
                                u"pilotName": "Johnny Dee",
                            }
                        ),
                        u"name": u"foo/2018-04-14-fla-6ng-01.igc",
                        u"trace": dict,
                        u"airspaces": [],
                    },
                    {
                        u"status": 2,
                        u"cacheKey": None,
                        u"flight": None,
                        u"name": u"__MACOSX/foo/._2018-04-14-fla-6ng-01.igc",
                        u"trace": None,
                        u"airspaces": None,
                    },
                    {
                        u"status": 0,
                        u"cacheKey": text_type,
                        u"flight": Partial(
                            {
                                u"club": None,
                                u"copilot": None,
                                u"copilotName": None,
                                u"distance": 195040,
                                u"igcFile": dict,
                                u"pilot": None,
                                u"pilotName": "Johnny Dee",
                            }
                        ),
                        u"name": u"792xaaa1.igc",
                        u"trace": dict,
                        u"airspaces": [],
                    },
                    {
                        u"status": 2,
                        u"cacheKey": None,
                        u"flight": None,
                        u"name": u"__MACOSX/._792xaaa1.igc",
                        u"trace": None,
                        u"airspaces": None,
                    },
                ]
            ),
        }
    )


def test_upload_multiple(db_session, client):
    john = users.john()
    db_session.add(john)
    db_session.commit()

    data = MultiDict()
    data.add("pilotName", "JD   ")
    data.add("files", (igcs.simple_path,))
    data.add("files", (igcs.hornet_path,))

    res = client.post("/flights/upload", headers=auth_for(john), data=data)
    assert res.status_code == 200
    assert res.json == S(
        {
            u"club_members": [],
            u"aircraft_models": [],
            u"results": ExactSequence(
                [
                    {
                        u"status": 0,
                        u"cacheKey": text_type,
                        u"flight": Partial(
                            {
                                u"club": None,
                                u"copilot": None,
                                u"copilotName": None,
                                u"distance": 7872,
                                u"igcFile": dict,
                                u"pilot": None,
                                u"pilotName": "JD",
                            }
                        ),
                        u"name": Match(r".*simple\.igc"),
                        u"trace": dict,
                        u"airspaces": [],
                    },
                    {
                        u"status": 0,
                        u"cacheKey": text_type,
                        u"flight": Partial(
                            {
                                u"club": None,
                                u"copilot": None,
                                u"copilotName": None,
                                u"distance": 171246,
                                u"igcFile": dict,
                                u"pilot": None,
                                u"pilotName": "JD",
                            }
                        ),
                        u"name": Match(r".*2018-04-14-fla-6ng-01\.igc"),
                        u"trace": dict,
                        u"airspaces": [],
                    },
                ]
            ),
        }
    )


def test_invalid_pilot_id(db_session, client):
    john = users.john()
    db_session.add(john)
    db_session.commit()

    data = dict(pilotId="abc", files=(igcs.simple_path,))

    res = client.post("/flights/upload", headers=auth_for(john), data=data)
    assert res.status_code == 422
    assert res.json == {
        u"error": u"validation-failed",
        u"fields": {u"pilotId": [u"Not a valid integer."]},
    }


def test_unknown_pilot_id(db_session, client):
    john = users.john()
    db_session.add(john)
    db_session.commit()

    data = dict(pilotId=42, files=(igcs.simple_path,))

    res = client.post("/flights/upload", headers=auth_for(john), data=data)
    assert res.status_code == 422
    assert res.json == {u"error": u"unknown-pilot"}


def test_missing_pilot_fields(db_session, client):
    john = users.john()
    db_session.add(john)
    db_session.commit()

    data = dict(files=(igcs.simple_path,))

    res = client.post("/flights/upload", headers=auth_for(john), data=data)
    assert res.status_code == 422
    assert res.json == {
        u"error": u"validation-failed",
        u"fields": {u"_schema": [u"Either pilotName or pilotId must be set"]},
    }


def test_upload_with_weglide(db_session, client):
    john = users.john()
    db_session.add(john)
    db_session.commit()

    data = dict(
        pilotId=john.id,
        weglideUserId="123",
        weglideBirthday="2020-01-07",
        files=(igcs.simple_path,),
    )

    with patch.object(tasks.upload_to_weglide, "delay", return_value=None) as mock:
        res = client.post("/flights/upload", headers=auth_for(john), data=data)

    mock.assert_called_once()
    assert len(mock.call_args.args) == 3
    assert mock.call_args.args[1] == 123
    assert mock.call_args.args[2] == "2020-01-07"

    assert res.status_code == 200
    assert res.json == S(
        {
            u"club_members": list,
            u"aircraft_models": list,
            u"results": ExactSequence(
                [
                    {
                        u"status": 0,
                        u"cacheKey": IsTrue(),
                        u"flight": Partial(
                            {
                                u"club": None,
                                u"copilot": None,
                                u"copilotName": None,
                                u"distance": 7872,
                                u"igcFile": Partial(
                                    {
                                        u"weglideStatus": 1,
                                        u"weglideData": None,
                                    }
                                ),
                                u"pilotName": None,
                                u"pilot": {
                                    u"id": john.id,
                                    u"name": john.name,
                                },
                            }
                        ),
                        u"name": Match(r".*simple.igc"),
                        u"trace": dict,
                        u"airspaces": [],
                    }
                ]
            ),
        }
    )
