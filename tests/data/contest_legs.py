from datetime import timedelta

from skylines.model import ContestLeg, Location


def first(flight, **kwargs):
    return ContestLeg(
        flight=flight,
        contest_type="olc_plus",
        trace_type="classic",
        distance=234833,
        cruise_height=-6491,
        cruise_distance=241148,
        cruise_duration=timedelta(seconds=7104),
        climb_height=6510,
        climb_duration=timedelta(seconds=5252),
        start_height=1234,
        end_height=1253,
        start_time=flight.takeoff_time + timedelta(minutes=5),
        end_time=flight.takeoff_time + timedelta(minutes=53),
        start_location=Location(51.4, 7.1),
        end_location=Location(52.5, 7.8),
    ).apply_kwargs(kwargs)


def empty(flight, **kwargs):
    return ContestLeg(
        flight=flight,
        contest_type="olc_plus",
        trace_type="classic",
        start_time=flight.takeoff_time + timedelta(minutes=61),
        end_time=flight.takeoff_time + timedelta(minutes=69),
    ).apply_kwargs(kwargs)
