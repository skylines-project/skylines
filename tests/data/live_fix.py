from skylines.model import TrackingFix


def create(pilot, time, latitude, longitude):
    """Creates a test fix for the passed pilot"""
    fix = TrackingFix(
        pilot=pilot,
        time=time,
        time_visible=time,
        track=0,
        ground_speed=10,
        airspeed=10,
        altitude=100,
        elevation=0,
        vario=0,
    )

    fix.set_location(latitude, longitude)

    return fix
