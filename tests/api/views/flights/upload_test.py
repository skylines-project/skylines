from pytest_voluptuous import S
from voluptuous.validators import ExactSequence, Datetime, Match, IsTrue
from werkzeug.datastructures import MultiDict

from skylines.lib.compat import text_type

from tests.api import auth_for
from tests.data import users, igcs


def test_upload(db_session, client):
    john = users.john()
    db_session.add(john)
    db_session.commit()

    data = dict(files=(igcs.simple_path,))

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
                            u"pilot": None,
                            u"distance": 7872,
                            u"igcFile": {
                                u"date": u"2011-06-18",
                                u"model": u"ASK13",
                                u"registration": u"LY-KDR",
                                u"competitionId": None,
                                u"filename": Match(r"simple(_\d+)?.igc"),
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

    data = dict(files=(igcs.zip_path,))

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
                        u"flight": {
                            u"pilotName": None,
                            u"takeoffAirport": None,
                            u"registration": u"D-9041",
                            u"speed": 16.25958982149639,
                            u"id": int,
                            u"privacyLevel": 2,
                            u"takeoffTime": u"2018-04-14T10:13:55+00:00",
                            u"score": 191.94581098298332,
                            u"scoreEndTime": u"2018-04-14T13:19:19+00:00",
                            u"copilot": None,
                            u"timeCreated": Datetime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
                            u"scoreStartTime": u"2018-04-14T10:16:51+00:00",
                            u"club": None,
                            u"scoreDate": u"2018-04-14T10:13:55",
                            u"landingTime": u"2018-04-14T13:19:19+00:00",
                            u"rawScore": 191.94581098298332,
                            u"copilotName": None,
                            u"pilot": None,
                            u"distance": 171246,
                            u"igcFile": {
                                u"date": u"2018-04-14",
                                u"model": u"Duo Discus (PAS)",
                                u"registration": u"D-9041",
                                u"competitionId": u"TH",
                                u"filename": Match(r"2018-04-14-fla-6ng-01.*\.igc"),
                            },
                            u"landingAirport": None,
                            u"triangleDistance": 68997,
                            u"model": None,
                            u"competitionId": u"TH",
                        },
                        u"name": u"foo/2018-04-14-fla-6ng-01.igc",
                        u"trace": {
                            u"barogram_h": text_type,
                            u"igc_end_time": u"2018-04-14T13:20:31+00:00",
                            u"enl": text_type,
                            u"elevations_h": text_type,
                            u"igc_start_time": u"2018-04-14T10:12:31+00:00",
                            u"barogram_t": text_type,
                        },
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
                        u"flight": {
                            u"pilotName": None,
                            u"takeoffAirport": None,
                            u"registration": u"F-CAEN",
                            u"speed": 21.54423947862587,
                            u"id": int,
                            u"privacyLevel": 2,
                            u"takeoffTime": u"2017-09-02T10:43:02+00:00",
                            u"score": 196.1458728865586,
                            u"scoreEndTime": u"2017-09-02T13:18:11+00:00",
                            u"copilot": None,
                            u"timeCreated": Datetime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
                            u"scoreStartTime": u"2017-09-02T10:45:48+00:00",
                            u"club": None,
                            u"scoreDate": u"2017-09-02T10:43:02",
                            u"landingTime": u"2017-09-02T13:18:11+00:00",
                            u"rawScore": 196.1458728865586,
                            u"copilotName": None,
                            u"pilot": None,
                            u"distance": 195040,
                            u"igcFile": {
                                u"date": u"2017-09-02",
                                u"model": None,
                                u"registration": u"F-CAEN",
                                u"competitionId": u"5L",
                                u"filename": Match(r"792xaaa1.*\.igc"),
                            },
                            u"landingAirport": None,
                            u"triangleDistance": 3685,
                            u"model": None,
                            u"competitionId": u"5L",
                        },
                        u"name": u"792xaaa1.igc",
                        u"trace": {
                            u"barogram_h": text_type,
                            u"igc_end_time": u"2017-09-02T13:18:46+00:00",
                            u"enl": text_type,
                            u"elevations_h": text_type,
                            u"igc_start_time": u"2017-09-02T10:38:17+00:00",
                            u"barogram_t": text_type,
                        },
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
                            u"pilot": None,
                            u"distance": 7872,
                            u"igcFile": {
                                u"date": u"2011-06-18",
                                u"model": u"ASK13",
                                u"registration": u"LY-KDR",
                                u"competitionId": None,
                                u"filename": Match(r"simple.*\.igc"),
                            },
                            u"landingAirport": None,
                            u"triangleDistance": 4003,
                            u"model": None,
                            u"competitionId": None,
                        },
                        u"name": Match(r".*simple\.igc"),
                        u"trace": {
                            u"barogram_h": text_type,
                            u"igc_end_time": u"2011-06-18T09:15:40+00:00",
                            u"enl": text_type,
                            u"elevations_h": text_type,
                            u"igc_start_time": u"2011-06-18T09:07:49+00:00",
                            u"barogram_t": text_type,
                        },
                        u"airspaces": [],
                    },
                    {
                        u"status": 0,
                        u"cacheKey": text_type,
                        u"flight": {
                            u"pilotName": None,
                            u"takeoffAirport": None,
                            u"registration": u"D-9041",
                            u"speed": 16.25958982149639,
                            u"id": int,
                            u"privacyLevel": 2,
                            u"takeoffTime": u"2018-04-14T10:13:55+00:00",
                            u"score": 191.94581098298332,
                            u"scoreEndTime": u"2018-04-14T13:19:19+00:00",
                            u"copilot": None,
                            u"timeCreated": Datetime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
                            u"scoreStartTime": u"2018-04-14T10:16:51+00:00",
                            u"club": None,
                            u"scoreDate": u"2018-04-14T10:13:55",
                            u"landingTime": u"2018-04-14T13:19:19+00:00",
                            u"rawScore": 191.94581098298332,
                            u"copilotName": None,
                            u"pilot": None,
                            u"distance": 171246,
                            u"igcFile": {
                                u"date": u"2018-04-14",
                                u"model": u"Duo Discus (PAS)",
                                u"registration": u"D-9041",
                                u"competitionId": u"TH",
                                u"filename": Match(r"2018-04-14-fla-6ng-01.*\.igc"),
                            },
                            u"landingAirport": None,
                            u"triangleDistance": 68997,
                            u"model": None,
                            u"competitionId": u"TH",
                        },
                        u"name": Match(r".*2018-04-14-fla-6ng-01\.igc"),
                        u"trace": {
                            u"barogram_h": text_type,
                            u"igc_end_time": u"2018-04-14T13:20:31+00:00",
                            u"enl": text_type,
                            u"elevations_h": text_type,
                            u"igc_start_time": u"2018-04-14T10:12:31+00:00",
                            u"barogram_t": text_type,
                        },
                        u"airspaces": [],
                    },
                ]
            ),
        }
    )
