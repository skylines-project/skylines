from skylines.model import AircraftModel


def hornet(**kwargs):
    return AircraftModel(
        name='Hornet',
        kind=1,
        igc_index=100,
        dmst_index=100,
        **kwargs
    )
