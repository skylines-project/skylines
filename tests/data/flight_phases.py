from datetime import timedelta

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
