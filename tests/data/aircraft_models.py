# coding=utf-8

from skylines.model import AircraftModel


def hornet(**kwargs):
    return AircraftModel(
        name='Hornet',
        kind=1,
        igc_index=100,
        dmst_index=100,
        **kwargs
    )


def nimeta(**kwargs):
    return AircraftModel(
        name='Nimeta',
        kind=1,
        igc_index=142,
        dmst_index=112,
        **kwargs
    )


def ask13(**kwargs):
    return AircraftModel(
        name='ASK 13',
        igc_index=42,
        dmst_index=17,
        **kwargs
    )


def dimona(**kwargs):
    return AircraftModel(
        name='Dimona',
        kind=2,
        **kwargs
    )


def epsilon(**kwargs):
    return AircraftModel(
        name='EPSILON',
        kind=3,
        **kwargs
    )


def delta(**kwargs):
    return AircraftModel(
        name=u'Δ',
        kind=4,
        **kwargs
    )


def falcon9(**kwargs):
    return AircraftModel(
        name='Falcon 9',
        kind=5,
        **kwargs
    )
