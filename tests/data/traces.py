from datetime import timedelta, datetime

from skylines.model import Trace, Location


def olc_classic(flight, **kwargs):
    return Trace(
        flight=flight,
        contest_type="olc_plus",
        trace_type="classic",
        distance=725123,
        duration=timedelta(hours=6.53),
        times=[
            datetime(2016, 8, 17, 9, 53, 22),
            datetime(2016, 8, 17, 11, 32, 29),
            datetime(2016, 8, 17, 14, 2, 54),
            datetime(2016, 8, 17, 16, 43, 43),
        ],
        locations=[
            Location(51.3, 7.1),
            Location(51.6, 9.3),
            Location(50.2, 5.8),
            Location(51.3, 7.1),
        ],
    ).apply_kwargs(kwargs)
