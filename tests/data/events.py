from datetime import datetime

from skylines.model import Event


def flight_comment(actor, flight, flight_comment, **kwargs):
    return Event(
        type=Event.Type.FLIGHT_COMMENT,
        time=datetime(2017, 02, 11, 12, 34, 56),
        actor=actor,
        flight=flight,
        flight_comment=flight_comment,
    ).apply_kwargs(kwargs)


def flight(actor, flight, **kwargs):
    return Event(
        type=Event.Type.FLIGHT,
        time=datetime(2017, 02, 12, 12, 34, 56),
        actor=actor,
        flight=flight,
    ).apply_kwargs(kwargs)


def follower(actor, user, **kwargs):
    return Event(
        type=Event.Type.FOLLOWER,
        time=datetime(2017, 02, 13, 12, 34, 56),
        actor=actor,
        user=user,
    ).apply_kwargs(kwargs)


def new_user(actor, **kwargs):
    return Event(
        type=Event.Type.NEW_USER,
        time=datetime(2017, 02, 14, 12, 34, 56),
        actor=actor,
    ).apply_kwargs(kwargs)


def club_join(actor, club, **kwargs):
    return Event(
        type=Event.Type.CLUB_JOIN,
        time=datetime(2017, 02, 15, 12, 34, 56),
        actor=actor,
        club=club,
    ).apply_kwargs(kwargs)
