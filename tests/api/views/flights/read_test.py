from tests.data import add_fixtures, igcs, flights, clubs, users


def test_basic_flight(db_session, client):
    john = users.john(club=clubs.lva())
    flight = flights.one(pilot=john, igc_file=igcs.simple(owner=john))
    add_fixtures(db_session, flight)

    res = client.get('/flights/{id}'.format(id=flight.id))
    assert res.status_code == 200
    print res.json
    assert res.json == {
        u'flight': {
            u'id': flight.id,
            u'timeCreated': u'2011-06-19T11:23:45+00:00',
            u'pilot': {
                u'id': john.id,
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
                    u'id': john.id,
                    u'name': u'John Doe'
                },
                u'filename': u'simple.igc',
                u'registration': None,
                u'competitionId': None,
                u'model': None,
                u'date': u'2011-06-18',
            },
        }
    }


def test_filled_flight(db_session, client):
    lva = clubs.lva()
    john = users.john(club=lva)
    flight = flights.filled(pilot=john, co_pilot_name='jane', club=lva, igc_file=igcs.filled(owner=john))
    add_fixtures(db_session, flight)

    res = client.get('/flights/{id}'.format(id=flight.id))
    assert res.status_code == 200
    print res.json
    assert res.json == {
        u'flight': {
            u'id': flight.id,
            u'timeCreated': u'2016-12-30T11:23:45+00:00',
            u'pilot': {
                u'id': john.id,
                u'name': u'John Doe'
            },
            u'pilotName': None,
            u'copilot': None,
            u'copilotName': u'jane',
            u'club': {
                u'id': lva.id,
                u'name': u'LV Aachen',
            },
            u'model': None,
            u'registration': u'D-1234',
            u'competitionId': u'701',
            u'scoreDate': u'2011-06-18',
            u'takeoffTime': u'2016-12-30T11:12:23+00:00',
            u'scoreStartTime': u'2016-12-30T11:17:23+00:00',
            u'scoreEndTime': u'2016-12-30T16:04:40+00:00',
            u'landingTime': u'2016-12-30T16:15:40+00:00',
            u'takeoffAirport': None,
            u'landingAirport': None,
            u'distance': 512,
            u'triangleDistance': 432,
            u'rawScore': 799.0,
            u'score': 799.0,
            u'speed': None,
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
