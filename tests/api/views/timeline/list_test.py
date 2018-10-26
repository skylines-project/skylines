from tests.data import (
    add_fixtures,
    events,
    users,
    flights,
    flight_comments,
    clubs,
    igcs,
)


def test_event_types(db_session, client):
    john = users.john()
    jane = users.jane()
    lva = clubs.lva()
    add_fixtures(db_session, john, jane, lva)

    flight = flights.one(igc_file=igcs.simple(owner=john))
    flight_comment = flight_comments.emoji(flight=flight, user=john)
    add_fixtures(db_session, flight, flight_comment)

    flight_event = events.flight(flight)
    flight_comment_event = events.flight_comment(flight_comment)
    follower_event = events.follower(actor=john, user=jane)
    new_user_event = events.new_user(jane)
    club_join_event = events.club_join(actor=john, club=lva)
    add_fixtures(
        db_session,
        flight_event,
        flight_comment_event,
        follower_event,
        new_user_event,
        club_join_event,
    )

    res = client.get("/timeline")
    assert res.status_code == 200
    assert res.json == {
        "events": [
            {
                "id": club_join_event.id,
                "type": "club-join",
                "time": "2017-02-15T12:34:56+00:00",
                "actor": {"id": john.id, "name": "John Doe"},
                "club": {"id": club_join_event.club.id, "name": "LV Aachen"},
            },
            {
                "id": new_user_event.id,
                "type": "new-user",
                "time": "2017-02-14T12:34:56+00:00",
                "actor": {"id": jane.id, "name": "Jane Doe"},
            },
            {
                "id": follower_event.id,
                "type": "follower",
                "time": "2017-02-13T12:34:56+00:00",
                "actor": {"id": john.id, "name": "John Doe"},
                "user": {"id": jane.id, "name": "Jane Doe"},
            },
            {
                "id": flight_event.id,
                "type": "flight-upload",
                "time": "2017-02-12T12:34:56+00:00",
                "actor": {"id": john.id, "name": "John Doe"},
                "flight": {
                    "id": flight.id,
                    "date": "2011-06-18",
                    "pilot_id": john.id,
                    "copilot_id": None,
                    "distance": None,
                },
            },
            {
                "id": flight_comment_event.id,
                "type": "flight-comment",
                "time": "2017-02-11T12:34:56+00:00",
                "actor": {"id": john.id, "name": "John Doe"},
                "flightComment": {"id": flight_comment.id},
                "flight": {
                    "id": flight.id,
                    "date": "2011-06-18",
                    "pilot_id": john.id,
                    "copilot_id": None,
                    "distance": None,
                },
            },
        ]
    }


def test_paging(db_session, client):
    john = users.john()
    for _ in range(75):
        event = events.new_user(actor=john)
        db_session.add(event)

    db_session.commit()

    res = client.get("/timeline")
    assert res.status_code == 200
    assert len(res.json["events"]) == 50

    res = client.get("/timeline?page=2")
    assert res.status_code == 200
    assert len(res.json["events"]) == 25

    res = client.get("/timeline?page=3")
    assert res.status_code == 200
    assert len(res.json["events"]) == 0

    res = client.get("/timeline?per_page=40")
    assert res.status_code == 200
    assert len(res.json["events"]) == 40

    res = client.get("/timeline?per_page=40&page=2")
    assert res.status_code == 200
    assert len(res.json["events"]) == 35
