from datetime import datetime

from skylines.model import FlightMeetings
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
)


def expected_basic_flight_json(flight):
    return {
        u'id': flight.id,
        u'timeCreated': u'2011-06-19T11:23:45+00:00',
        u'pilot': {
            u'id': flight.pilot.id,
            u'name': u'John Doe'
        },
        u'pilotName': None,
        u'copilot': None,
        u'copilotName': None,
        u'club': None,
        u'model': None,
        u'registration': None,
        u'competitionId': None,
        u'scoreDate': u'2011-06-18',
        u'takeoffTime': u'2011-06-18T09:11:23+00:00',
        u'scoreStartTime': None,
        u'scoreEndTime': None,
        u'landingTime': u'2011-06-18T09:15:40+00:00',
        u'takeoffAirport': None,
        u'landingAirport': None,
        u'distance': None,
        u'triangleDistance': None,
        u'rawScore': None,
        u'score': None,
        u'speed': None,
        u'privacyLevel': 0,
        u'igcFile': {
            u'owner': {
                u'id': flight.igc_file.owner.id,
                u'name': u'John Doe'
            },
            u'filename': u'simple.igc',
            u'registration': None,
            u'competitionId': None,
            u'model': None,
            u'date': u'2011-06-18',
        },
    }


def test_basic_flight(db_session, client):
    flight = flights.one(igc_file=igcs.simple(owner=users.john()))
    add_fixtures(db_session, flight)

    res = client.get('/flights/{id}'.format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u'flight': expected_basic_flight_json(flight),
    }


def test_filled_flight(db_session, client):
    lva = clubs.lva()
    john = users.john(club=lva)
    jane = users.jane()
    flight = flights.filled(
        pilot=john,
        pilot_name='johnny_d',
        co_pilot=jane,
        co_pilot_name='jane',
        club=lva,
        model=aircraft_models.nimeta(),
        takeoff_airport=airports.meiersberg(),
        landing_airport=airports.merzbrueck(),
        igc_file=igcs.filled(owner=john)
    )
    add_fixtures(db_session, flight, traces.olc_classic(flight=flight))

    res = client.get('/flights/{id}'.format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u'flight': {
            u'id': flight.id,
            u'timeCreated': u'2016-12-30T11:23:45+00:00',
            u'pilot': {
                u'id': john.id,
                u'name': u'John Doe'
            },
            u'pilotName': u'johnny_d',
            u'copilot': {
                u'id': jane.id,
                u'name': u'Jane Doe'
            },
            u'copilotName': u'jane',
            u'club': {
                u'id': lva.id,
                u'name': u'LV Aachen',
            },
            u'model': {
                u'id': flight.model_id,
                u'name': u'Nimeta',
                u'type': u'glider',
                u'index': 112,
            },
            u'registration': u'D-1234',
            u'competitionId': u'701',
            u'scoreDate': u'2011-06-18',
            u'takeoffTime': u'2016-12-30T11:12:23+00:00',
            u'scoreStartTime': u'2016-12-30T11:17:23+00:00',
            u'scoreEndTime': u'2016-12-30T16:04:40+00:00',
            u'landingTime': u'2016-12-30T16:15:40+00:00',
            u'takeoffAirport': {
                u'id': flight.takeoff_airport.id,
                u'name': u'Meiersberg',
                u'countryCode': u'DE'
            },
            u'landingAirport': {
                u'id': flight.landing_airport.id,
                u'name': u'Aachen Merzbruck',
                u'countryCode': u'DE',
            },
            u'distance': 512,
            u'triangleDistance': 432,
            u'rawScore': 799.0,
            u'score': 713.0,
            u'speed': 30.84579717542964,
            u'privacyLevel': 0,
            u'igcFile': {
                u'owner': {
                    u'id': john.id,
                    u'name': u'John Doe'
                },
                u'filename': u'abc1234d.igc',
                u'registration': u'D-4449',
                u'competitionId': u'TH',
                u'model': u'Hornet',
                u'date': u'2017-01-15',
            },
        }
    }


def test_empty_extended(db_session, client):
    flight = flights.one(igc_file=igcs.simple(owner=users.john()))
    add_fixtures(db_session, flight)

    res = client.get('/flights/{id}?extended'.format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u'flight': expected_basic_flight_json(flight),
        u'near_flights': [],
        u'comments': [],
        u'contest_legs': {
            u'classic': [],
            u'triangle': [],
        },
        u'phases': [],
        u'performance': {
            u'circling': [],
            u'cruise': {},
        },
    }


def test_comments(db_session, client):
    flight = flights.one(igc_file=igcs.simple(owner=users.john()))
    comment1 = flight_comments.yeah(flight=flight)
    comment2 = flight_comments.emoji(flight=flight)
    comment3 = flight_comments.yeah(flight=flight, user=flight.igc_file.owner, text='foo')
    comment4 = flight_comments.yeah(flight=flight, text='bar')
    comment5 = flight_comments.yeah(flight=flight, user=users.jane(), text='baz')
    add_fixtures(db_session, flight, comment1, comment2, comment3, comment4, comment5)

    res = client.get('/flights/{id}?extended'.format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u'flight': expected_basic_flight_json(flight),
        u'near_flights': [],
        u'comments': [{
            u'user': None,
            u'text': u'Yeah!',
        }, {
            u'user': None,
            u'text': u'\U0001f44d',
        }, {
            u'user': {
                u'id': comment3.user.id,
                u'name': u'John Doe'
            },
            u'text': u'foo',
        }, {
            u'user': None,
            u'text': u'bar',
        }, {
            u'user': {
                u'id': comment5.user.id,
                u'name': u'Jane Doe'
            },
            u'text': u'baz',
        }],
        u'contest_legs': {
            u'classic': [],
            u'triangle': [],
        },
        u'phases': [],
        u'performance': {
            u'circling': [],
            u'cruise': {},
        },
    }


def test_meetings(db_session, client):
    flight = flights.one(igc_file=igcs.simple(owner=users.john()))
    flight2 = flights.one(igc_file=igcs.simple(owner=users.jane(), md5='foobar'))
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

    res = client.get('/flights/{id}?extended'.format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u'flight': expected_basic_flight_json(flight),
        u'near_flights': [{
            u'flight': {
                u'id': flight2.id,
                u'pilot': {
                    u'id': flight2.pilot.id,
                    u'name': u'Jane Doe',
                },
                u'pilotName': None,
                u'copilot': None,
                u'copilotName': None,
                u'model': None,
                u'registration': None,
                u'competitionId': None,
                u'igcFile': {
                    u'filename': u'simple.igc',
                    u'date': u'2011-06-18',
                    u'registration': None,
                    u'owner': {
                        u'id': flight2.igc_file.owner.id,
                        u'name': u'Jane Doe',
                    },
                    u'model': None,
                    u'competitionId': None,
                },
            },
            u'times': [{
                u'start': u'2016-04-03T12:34:56+00:00',
                u'end': u'2016-04-03T12:38:01+00:00',
            }, {
                u'start': u'2016-04-03T12:56:36+00:00',
                u'end': u'2016-04-03T13:01:31+00:00',
            }],
        }],
        u'comments': [],
        u'contest_legs': {
            u'classic': [],
            u'triangle': [],
        },
        u'phases': [],
        u'performance': {
            u'circling': [],
            u'cruise': {},
        },
    }


def test_contest_legs(db_session, client):
    flight = flights.one(igc_file=igcs.simple(owner=users.john()))
    leg1 = contest_legs.first(flight=flight)
    leg2 = contest_legs.empty(flight=flight)
    leg3 = contest_legs.first(flight=flight, trace_type='triangle')
    add_fixtures(db_session, flight, leg1, leg2, leg3)

    res = client.get('/flights/{id}?extended'.format(id=flight.id))
    assert res.status_code == 200
    assert res.json == {
        u'flight': expected_basic_flight_json(flight),
        u'near_flights': [],
        u'comments': [],
        u'contest_legs': {
            u'classic': [{
                u'distance': 234833.0,
                u'duration': 2880,
                u'start': 33383,
                u'climbDuration': 5252,
                u'climbHeight': 6510.0,
                u'cruiseDistance': 241148.0,
                u'cruiseHeight': -6491.0,
            }, {
                u'distance': None,
                u'duration': 480,
                u'start': 36743,
                u'climbDuration': None,
                u'climbHeight': None,
                u'cruiseDistance': None,
                u'cruiseHeight': None,
            }],
            u'triangle': [{
                u'distance': 234833.0,
                u'duration': 2880,
                u'start': 33383,
                u'climbDuration': 5252,
                u'climbHeight': 6510.0,
                u'cruiseDistance': 241148.0,
                u'cruiseHeight': -6491.0,
            }],
        },
        u'phases': [],
        u'performance': {
            u'circling': [],
            u'cruise': {},
        },
    }
