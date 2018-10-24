from datetime import datetime

from skylines.model import Event


def flight_comment(flight_comment, **kwargs):
    return (
        Event.for_flight_comment(flight_comment)
        .apply_kwargs(dict(time=datetime(2017, 2, 11, 12, 34, 56)))
        .apply_kwargs(kwargs)
    )


def flight(flight, **kwargs):
    return (
        Event.for_flight(flight)
        .apply_kwargs(dict(time=datetime(2017, 2, 12, 12, 34, 56)))
        .apply_kwargs(kwargs)
    )


def follower(actor, user, **kwargs):
    return (
        Event.for_follower(user, actor)
        .apply_kwargs(dict(time=datetime(2017, 2, 13, 12, 34, 56)))
        .apply_kwargs(kwargs)
    )


def new_user(actor, **kwargs):
    return (
        Event.for_new_user(actor)
        .apply_kwargs(dict(time=datetime(2017, 2, 14, 12, 34, 56)))
        .apply_kwargs(kwargs)
    )


def club_join(actor, club, **kwargs):
    return (
        Event.for_club_join(club.id, actor)
        .apply_kwargs(dict(time=datetime(2017, 2, 15, 12, 34, 56)))
        .apply_kwargs(kwargs)
    )
