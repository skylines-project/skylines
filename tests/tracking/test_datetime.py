from datetime import time

from skylines.tracking.datetime import ms_to_time


def test_ms_to_time():
    assert ms_to_time(0) == time(0, 0, 0)

    assert ms_to_time(12 * 60 * 60 * 1000 + 34 * 60 * 1000 + 56 * 1000 + 789) == time(
        12, 34, 56, 789
    )

    assert ms_to_time(123.789) == time(0, 0, 0, 123)
