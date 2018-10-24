# coding=utf-8

from datetime import datetime

from skylines.model import FlightComment


def yeah(flight, **kwargs):
    return FlightComment(
        time_created=datetime(2017, 1, 19, 12, 34, 56), flight=flight, text=u"Yeah!"
    ).apply_kwargs(kwargs)


def emoji(flight, **kwargs):
    return FlightComment(
        time_created=datetime(2020, 12, 19, 12, 34, 56), flight=flight, text=u"👍"
    ).apply_kwargs(kwargs)
