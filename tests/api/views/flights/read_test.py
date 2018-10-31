from datetime import datetime

from pytest_voluptuous import S
from voluptuous.validators import Unordered

from skylines.model import FlightMeetings, Flight
from tests.api import auth_for
from tests.voluptuous import Approx
from tests.data import (
    add_fixtures,
    igcs,
    flights,
    clubs,
    users,
    aircraft_models,
    airports,
    traces,
    flight_comments,
    contest_legs,
    flight_phases,
)


def expected_basic_flight_json(flight):
    return {
        u"id": flight.id,
        u"timeCreated": u"2011-06-19T11:23:45+00:00",
        u"pilot": {u"id": flight.pilot.id, u"name": u"John Doe"},
        u"pilotName": None,
        u"copilot": None,
        u"copilotName": None,
        u"club": None,
        u"model": None,
        u"registration": None,
        u"competitionId": None,
        u"scoreDate": u"2011-06-18",
        u"takeoffTime": u"2011-06-18T09:11:23+00:00",
        u"scoreStartTime": None,
        u"scoreEndTime": None,
        u"landingTime": u"2011-06-18T09:15:40+00:00",
        u"takeoffAirport": None,
        u"landingAirport": None,
        u"distance": None,
        u"triangleDistance": None,
        u"rawScore": None,
        u"score": None,
        u"speed": None,
        u"privacyLevel": 0,
        u"igcFile": {
            u"owner": {u"id": flight.igc_file.owner.id, u"name": u"John Doe"},
            u"filename": u"simple.igc",
            u"registration": None,
            u"competitionId": None,
            u"model": None,
            u"date": u"2011-06-18",
        },
    }


def test_basic_flight(db_session, client):
    flight = flights.one(igc_file=igcs.simple(owner=users.john()))
    add_fixtures(db_session, flight)

    res = client.get("/flights/{id}".format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {u"flight": expected_basic_flight_json(flight)}


def test_basic_flight_json(db_session, client):
    # add user
    john = users.john()
    db_session.add(john)
    db_session.commit()

    # upload flight
    data = dict(files=(igcs.simple_path,))
    res = client.post("/flights/upload", headers=auth_for(john), data=data)
    assert res.status_code == 200
    flight_id = res.json["results"][0]["flight"]["id"]

    res = client.get("/flights/{id}/json".format(id=flight_id), headers=auth_for(john))
    assert res.status_code == 200
    assert res.json == S(
        {
            u"additional": {
                u"competition_id": None,
                u"model": None,
                u"registration": u"LY-KDR",
            },
            u"barogram_h": u"cH??D?EKOk@o@U}@k@OGUIEg@c@S[KIKKKI[]_@a@WSGYQk@",
            u"barogram_t": u"ik_A{B{@gASISSg@]S]]IIIIMIIISIIISIIIIIIIIIIII",
            u"contests": Unordered(
                [
                    {
                        u"name": u"olc_plus triangle",
                        u"times": u"{y_AgBeAyAS",
                        u"turnpoints": u"mejkIyljwC~_@{y@}~@dp@|j@t{AnEgJ",
                    },
                    {
                        u"name": u"olc_plus classic",
                        u"times": u"ur_AeHg@]g@eAg@",
                        u"turnpoints": u"ypokI{wowCdsEhzDyFcjAu_@]g^bq@v[d{AtTwI",
                    },
                ]
            ),
            u"elevations_h": u"",
            u"elevations_t": u"",
            u"enl": u"",
            u"geoid": Approx(25.15502072293512),
            u"points": u"syokIm|owC????lYxKbQrIrGlBlPjH|N`Kn[l[tRjZ~LrPpRz^tP|`@lFnHrG`CvGz@xDYjCiI`@cQq@mVgBmQgFwVcNjAkMhDuHrGwNrWyDzOOzPh@fQ`B~OpCfMxDbJxEtGtF~CrFz@pFk@`CsAlAsG",
            u"sfid": int,
        }
    )


def test_filled_flight(db_session, client):
    lva = clubs.lva()
    john = users.john(club=lva)
    jane = users.jane()
    flight = flights.filled(
        pilot=john,
        pilot_name=u"johnny_d",
        co_pilot=jane,
        co_pilot_name=u"jane",
        club=lva,
        model=aircraft_models.nimeta(),
        takeoff_airport=airports.meiersberg(),
        landing_airport=airports.merzbrueck(),
        igc_file=igcs.filled(owner=john),
    )
    add_fixtures(db_session, flight, traces.olc_classic(flight=flight))

    res = client.get("/flights/{id}".format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u"flight": {
            u"id": flight.id,
            u"timeCreated": u"2016-12-30T11:23:45+00:00",
            u"pilot": {u"id": john.id, u"name": u"John Doe"},
            u"pilotName": u"johnny_d",
            u"copilot": {u"id": jane.id, u"name": u"Jane Doe"},
            u"copilotName": u"jane",
            u"club": {u"id": lva.id, u"name": u"LV Aachen"},
            u"model": {
                u"id": flight.model_id,
                u"name": u"Nimeta",
                u"type": u"glider",
                u"index": 112,
            },
            u"registration": u"D-1234",
            u"competitionId": u"701",
            u"scoreDate": u"2011-06-18",
            u"takeoffTime": u"2016-12-30T11:12:23+00:00",
            u"scoreStartTime": u"2016-12-30T11:17:23+00:00",
            u"scoreEndTime": u"2016-12-30T16:04:40+00:00",
            u"landingTime": u"2016-12-30T16:15:40+00:00",
            u"takeoffAirport": {
                u"id": flight.takeoff_airport.id,
                u"name": u"Meiersberg",
                u"countryCode": u"DE",
            },
            u"landingAirport": {
                u"id": flight.landing_airport.id,
                u"name": u"Aachen Merzbruck",
                u"countryCode": u"DE",
            },
            u"distance": 512,
            u"triangleDistance": 432,
            u"rawScore": 799.0,
            u"score": 713.3928571428571,
            u"speed": 30.84579717542964,
            u"privacyLevel": 0,
            u"igcFile": {
                u"owner": {u"id": john.id, u"name": u"John Doe"},
                u"filename": u"abc1234d.igc",
                u"registration": u"D-4449",
                u"competitionId": u"TH",
                u"model": u"Hornet",
                u"date": u"2017-01-15",
            },
        }
    }


def test_empty_extended(db_session, client):
    flight = flights.one(igc_file=igcs.simple(owner=users.john()))
    add_fixtures(db_session, flight)

    res = client.get("/flights/{id}?extended".format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u"flight": expected_basic_flight_json(flight),
        u"near_flights": [],
        u"comments": [],
        u"contest_legs": {u"classic": [], u"triangle": []},
        u"phases": [],
        u"performance": {u"circling": [], u"cruise": {}},
    }


def test_comments(db_session, client):
    flight = flights.one(igc_file=igcs.simple(owner=users.john()))
    comment1 = flight_comments.yeah(flight=flight)
    comment2 = flight_comments.emoji(flight=flight)
    comment3 = flight_comments.yeah(
        flight=flight, user=flight.igc_file.owner, text=u"foo"
    )
    comment4 = flight_comments.yeah(flight=flight, text=u"bar")
    comment5 = flight_comments.yeah(flight=flight, user=users.jane(), text=u"baz")
    add_fixtures(db_session, flight, comment1, comment2, comment3, comment4, comment5)

    res = client.get("/flights/{id}?extended".format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u"flight": expected_basic_flight_json(flight),
        u"near_flights": [],
        u"comments": [
            {u"user": None, u"text": u"Yeah!"},
            {u"user": None, u"text": u"\U0001f44d"},
            {u"user": {u"id": comment3.user.id, u"name": u"John Doe"}, u"text": u"foo"},
            {u"user": None, u"text": u"bar"},
            {u"user": {u"id": comment5.user.id, u"name": u"Jane Doe"}, u"text": u"baz"},
        ],
        u"contest_legs": {u"classic": [], u"triangle": []},
        u"phases": [],
        u"performance": {u"circling": [], u"cruise": {}},
    }


def test_meetings(db_session, client):
    flight = flights.one(igc_file=igcs.simple(owner=users.john()))
    flight2 = flights.one(igc_file=igcs.simple(owner=users.jane(), md5="foobar"))
    meeting1 = FlightMeetings(
        source=flight,
        destination=flight2,
        start_time=datetime(2016, 4, 3, 12, 34, 56),
        end_time=datetime(2016, 4, 3, 12, 38, 1),
    )
    meeting2 = FlightMeetings(
        source=flight2,
        destination=flight,
        start_time=datetime(2016, 4, 3, 12, 56, 36),
        end_time=datetime(2016, 4, 3, 13, 1, 31),
    )
    add_fixtures(db_session, flight, flight2, meeting1, meeting2)

    res = client.get("/flights/{id}?extended".format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u"flight": expected_basic_flight_json(flight),
        u"near_flights": [
            {
                u"flight": {
                    u"id": flight2.id,
                    u"pilot": {u"id": flight2.pilot.id, u"name": u"Jane Doe"},
                    u"pilotName": None,
                    u"copilot": None,
                    u"copilotName": None,
                    u"model": None,
                    u"registration": None,
                    u"competitionId": None,
                    u"igcFile": {
                        u"filename": u"simple.igc",
                        u"date": u"2011-06-18",
                        u"registration": None,
                        u"owner": {
                            u"id": flight2.igc_file.owner.id,
                            u"name": u"Jane Doe",
                        },
                        u"model": None,
                        u"competitionId": None,
                    },
                },
                u"times": [
                    {
                        u"start": u"2016-04-03T12:34:56+00:00",
                        u"end": u"2016-04-03T12:38:01+00:00",
                    },
                    {
                        u"start": u"2016-04-03T12:56:36+00:00",
                        u"end": u"2016-04-03T13:01:31+00:00",
                    },
                ],
            }
        ],
        u"comments": [],
        u"contest_legs": {u"classic": [], u"triangle": []},
        u"phases": [],
        u"performance": {u"circling": [], u"cruise": {}},
    }


def test_contest_legs(db_session, client):
    flight = flights.one(igc_file=igcs.simple(owner=users.john()))
    leg1 = contest_legs.first(flight=flight)
    leg2 = contest_legs.empty(flight=flight)
    leg3 = contest_legs.first(flight=flight, trace_type="triangle")
    add_fixtures(db_session, flight, leg1, leg2, leg3)

    res = client.get("/flights/{id}?extended".format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u"flight": expected_basic_flight_json(flight),
        u"near_flights": [],
        u"comments": [],
        u"contest_legs": {
            u"classic": [
                {
                    u"distance": 234833.0,
                    u"duration": 2880,
                    u"start": 33383,
                    u"climbDuration": 5252,
                    u"climbHeight": 6510.0,
                    u"cruiseDistance": 241148.0,
                    u"cruiseHeight": -6491.0,
                },
                {
                    u"distance": None,
                    u"duration": 480,
                    u"start": 36743,
                    u"climbDuration": None,
                    u"climbHeight": None,
                    u"cruiseDistance": None,
                    u"cruiseHeight": None,
                },
            ],
            u"triangle": [
                {
                    u"distance": 234833.0,
                    u"duration": 2880,
                    u"start": 33383,
                    u"climbDuration": 5252,
                    u"climbHeight": 6510.0,
                    u"cruiseDistance": 241148.0,
                    u"cruiseHeight": -6491.0,
                }
            ],
        },
        u"phases": [],
        u"performance": {u"circling": [], u"cruise": {}},
    }


def test_performance(db_session, client):
    flight = flights.one(igc_file=igcs.simple(owner=users.john()))
    add_fixtures(
        db_session,
        flight,
        flight_phases.cruise(flight=flight),
        flight_phases.circling(flight=flight),
        flight_phases.circling_left(flight=flight),
        flight_phases.circling_right(flight=flight),
        flight_phases.circling_mixed(flight=flight),
    )

    res = client.get("/flights/{id}?extended".format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u"flight": expected_basic_flight_json(flight),
        u"near_flights": [],
        u"comments": [],
        u"contest_legs": {u"classic": [], u"triangle": []},
        u"phases": [],
        u"performance": {
            u"circling": [
                {
                    u"circlingDirection": u"total",
                    u"duration": 14472,
                    u"altDiff": 19543.0,
                    u"vario": 1.35046987285793,
                    u"fraction": 37.0,
                    u"count": 78,
                },
                {
                    u"circlingDirection": u"left",
                    u"duration": 3776,
                    u"altDiff": 5335.0,
                    u"vario": 1.41313559322034,
                    u"fraction": 26.0,
                    u"count": 17,
                },
                {
                    u"circlingDirection": u"right",
                    u"duration": 7900,
                    u"altDiff": 11344.0,
                    u"vario": 1.43607594936709,
                    u"fraction": 55.0,
                    u"count": 54,
                },
                {
                    u"circlingDirection": u"mixed",
                    u"duration": 2796,
                    u"altDiff": 2863.0,
                    u"vario": 1.02396280400573,
                    u"fraction": 19.0,
                    u"count": 7,
                },
            ],
            u"cruise": {
                u"duration": 24312,
                u"altDiff": -20647.0,
                u"distance": 837677.0,
                u"vario": -0.849292530437643,
                u"speed": 34.4552944491395,
                u"glideRate": 40.5694071410054,
                u"fraction": 63.0,
                u"count": 79,
            },
        },
    }


def test_phases(db_session, client):
    flight = flights.one(
        igc_file=igcs.simple(owner=users.john()),
        takeoff_time=datetime(2016, 5, 4, 8, 12, 46),
    )
    add_fixtures(
        db_session,
        flight,
        flight_phases.example1(flight=flight),
        flight_phases.example2(flight=flight),
    )

    expected_flight = expected_basic_flight_json(flight)
    expected_flight["takeoffTime"] = "2016-05-04T08:12:46+00:00"

    res = client.get("/flights/{id}?extended".format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u"flight": expected_flight,
        u"near_flights": [],
        u"comments": [],
        u"contest_legs": {u"classic": [], u"triangle": []},
        u"phases": [
            {
                u"circlingDirection": u"right",
                u"type": u"circling",
                u"secondsOfDay": 64446,
                u"startTime": u"2016-05-04T17:54:06+00:00",
                u"duration": 300,
                u"altDiff": 417.0,
                u"distance": 7028.0,
                u"vario": 1.39000000000002,
                u"speed": 23.4293014168156,
                u"glideRate": -16.8556125300829,
            },
            {
                u"circlingDirection": None,
                u"type": u"cruise",
                u"secondsOfDay": 64746,
                u"startTime": u"2016-05-04T17:59:06+00:00",
                u"duration": 44,
                u"altDiff": -93.0,
                u"distance": 977.0,
                u"vario": -2.11363636363637,
                u"speed": 22.2232648999519,
                u"glideRate": 10.5142328558912,
            },
        ],
        u"performance": {u"circling": [], u"cruise": {}},
    }


def test_missing(db_session, client):
    res = client.get("/flights/10000000")
    assert res.status_code == 404
    assert res.json == {
        u"message": u"Sorry, there is no such record (10000000) in our database."
    }


def test_unauthenticated_access_on_private_flight(db_session, client):
    flight = flights.one(
        privacy_level=Flight.PrivacyLevel.PRIVATE,
        igc_file=igcs.simple(owner=users.john()),
    )
    add_fixtures(db_session, flight)

    res = client.get("/flights/{id}".format(id=flight.id))
    assert res.status_code == 404
    assert res.json == {}


def test_unfriendly_user_access_on_private_flight(db_session, client):
    jane = users.jane()
    flight = flights.one(
        privacy_level=Flight.PrivacyLevel.PRIVATE,
        igc_file=igcs.simple(owner=users.john()),
    )
    add_fixtures(db_session, flight, jane)

    res = client.get("/flights/{id}".format(id=flight.id), headers=auth_for(jane))
    assert res.status_code == 404
    assert res.json == {}


def test_igc_owner_access_on_private_flight(db_session, client):
    john = users.john()
    flight = flights.one(
        pilot=None,
        privacy_level=Flight.PrivacyLevel.PRIVATE,
        igc_file=igcs.simple(owner=john),
    )
    add_fixtures(db_session, flight, john)

    res = client.get("/flights/{id}".format(id=flight.id), headers=auth_for(john))
    assert res.status_code == 200
    assert "flight" in res.json


def test_pilot_access_on_private_flight(db_session, client):
    jane = users.jane()
    flight = flights.one(
        pilot=jane,
        privacy_level=Flight.PrivacyLevel.PRIVATE,
        igc_file=igcs.simple(owner=users.john()),
    )
    add_fixtures(db_session, flight, jane)

    res = client.get("/flights/{id}".format(id=flight.id), headers=auth_for(jane))
    assert res.status_code == 200
    assert "flight" in res.json


def test_manager_access_on_private_flight(db_session, client):
    jane = users.jane(admin=True)
    flight = flights.one(
        privacy_level=Flight.PrivacyLevel.PRIVATE,
        igc_file=igcs.simple(owner=users.john()),
    )
    add_fixtures(db_session, flight, jane)

    res = client.get("/flights/{id}".format(id=flight.id), headers=auth_for(jane))
    assert res.status_code == 200
    assert "flight" in res.json


def test_unauthenticated_access_on_link_only_flight(db_session, client):
    flight = flights.one(
        privacy_level=Flight.PrivacyLevel.LINK_ONLY,
        igc_file=igcs.simple(owner=users.john()),
    )
    add_fixtures(db_session, flight)

    res = client.get("/flights/{id}".format(id=flight.id))
    assert res.status_code == 200
    assert "flight" in res.json
