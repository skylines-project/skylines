# coding=utf-8

from skylines.model import AircraftModel


def hornet(**kwargs):
    return AircraftModel(
        name=u"Hornet", kind=1, igc_index=100, dmst_index=100
    ).apply_kwargs(kwargs)


def nimeta(**kwargs):
    return AircraftModel(
        name=u"Nimeta", kind=1, igc_index=142, dmst_index=112
    ).apply_kwargs(kwargs)


def ask13(**kwargs):
    return AircraftModel(name=u"ASK 13", igc_index=42, dmst_index=17).apply_kwargs(
        kwargs
    )


def dimona(**kwargs):
    return AircraftModel(name=u"Dimona", kind=2).apply_kwargs(kwargs)


def epsilon(**kwargs):
    return AircraftModel(name=u"EPSILON", kind=3).apply_kwargs(kwargs)


def delta(**kwargs):
    return AircraftModel(name=u"Δ", kind=4).apply_kwargs(kwargs)


def falcon9(**kwargs):
    return AircraftModel(name=u"Falcon 9", kind=5).apply_kwargs(kwargs)
