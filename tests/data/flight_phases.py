from datetime import timedelta, datetime

from skylines.model import FlightPhase


def cruise(flight, **kwargs):
    return FlightPhase(
        flight=flight,
        aggregate=True,
        phase_type=FlightPhase.PT_CRUISE,
        alt_diff=-20647.0,
        duration=timedelta(seconds=24312),
        fraction=63.0,
        distance=837677.0,
        speed=34.4552944491395,
        vario=-0.849292530437643,
        glide_rate=40.5694071410054,
        count=79,
    ).apply_kwargs(kwargs)


def circling(flight, **kwargs):
    return FlightPhase(
        flight=flight,
        aggregate=True,
        phase_type=FlightPhase.PT_CIRCLING,
        circling_direction=FlightPhase.CD_TOTAL,
        alt_diff=19543.0,
        duration=timedelta(seconds=14472),
        fraction=37.0,
        vario=1.35046987285793,
        count=78,
    ).apply_kwargs(kwargs)


def circling_left(flight, **kwargs):
    return FlightPhase(
        flight=flight,
        aggregate=True,
        phase_type=FlightPhase.PT_CIRCLING,
        circling_direction=FlightPhase.CD_LEFT,
        alt_diff=5335.0,
        duration=timedelta(seconds=3776),
        fraction=26.0,
        vario=1.41313559322034,
        count=17,
    ).apply_kwargs(kwargs)


def circling_right(flight, **kwargs):
    return FlightPhase(
        flight=flight,
        aggregate=True,
        phase_type=FlightPhase.PT_CIRCLING,
        circling_direction=FlightPhase.CD_RIGHT,
        alt_diff=11344.0,
        duration=timedelta(seconds=7900),
        fraction=55.0,
        vario=1.43607594936709,
        count=54,
    ).apply_kwargs(kwargs)


def circling_mixed(flight, **kwargs):
    return FlightPhase(
        flight=flight,
        aggregate=True,
        phase_type=FlightPhase.PT_CIRCLING,
        circling_direction=FlightPhase.CD_MIXED,
        alt_diff=2863.0,
        duration=timedelta(seconds=2796),
        fraction=19.0,
        vario=1.02396280400573,
        count=7,
    ).apply_kwargs(kwargs)


def example1(flight, **kwargs):
    return FlightPhase(
        flight=flight,
        start_time=datetime(2016, 5, 4, 17, 54, 6),
        end_time=datetime(2016, 5, 4, 17, 54, 6) + timedelta(seconds=300),
        aggregate=False,
        phase_type=FlightPhase.PT_CIRCLING,
        circling_direction=FlightPhase.CD_RIGHT,
        alt_diff=417.0,
        duration=timedelta(seconds=300),
        distance=7028.0,
        speed=23.4293014168156,
        vario=1.39000000000002,
        glide_rate=-16.8556125300829,
        count=1,
    ).apply_kwargs(kwargs)


def example2(flight, **kwargs):
    return FlightPhase(
        flight=flight,
        start_time=datetime(2016, 5, 4, 17, 59, 6),
        end_time=datetime(2016, 5, 4, 17, 59, 6) + timedelta(seconds=44),
        aggregate=False,
        phase_type=FlightPhase.PT_CRUISE,
        alt_diff=-93.0,
        duration=timedelta(seconds=44),
        distance=977.0,
        speed=22.2232648999519,
        vario=-2.11363636363637,
        glide_rate=10.5142328558912,
        count=1,
    ).apply_kwargs(kwargs)
