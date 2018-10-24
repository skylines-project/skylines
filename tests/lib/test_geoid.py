# -*- coding: utf-8 -*-

import pytest

from skylines.lib.geoid import egm96_height, load_geoid
from skylines.model.geo import Location


@pytest.fixture(scope="session", autouse=True)
def geoid():
    load_geoid()


def test_geoid():
    # test data from http://earth-info.nga.mil/GandG/wgs84/gravitymod/egm96/egm96.html
    assert egm96_height(Location(38.6281550, 269.7791550)) == pytest.approx(
        -31.629, abs=0.25
    )
    assert egm96_height(Location(-14.6212170, 305.0211140)) == pytest.approx(
        -2.966, abs=0.25
    )
    assert egm96_height(Location(46.8743190, 102.4487290)) == pytest.approx(
        -43.572, abs=0.25
    )
    assert egm96_height(Location(-23.6174460, 133.8747120)) == pytest.approx(
        15.868, abs=0.25
    )
    assert egm96_height(Location(38.6254730, 359.9995000)) == pytest.approx(
        50.065, abs=0.5
    )
    assert egm96_height(Location(-0.4667440, 0.0023000)) == pytest.approx(
        17.330, abs=0.25
    )
