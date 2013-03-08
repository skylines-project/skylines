# -*- coding: utf-8 -*-

import sys
import nose
from nose.tools import eq_, assert_dict_equal, assert_dict_contains_subset

import datetime
from skylines.lib.igc import read_igc_headers


def test_empty_file():
    eq_(read_igc_headers([]), {})


def test_logger_information():
    assert_dict_equal(read_igc_headers(['AFLA6NG']),
                      dict(manufacturer_id='FLA', logger_id='6NG'))


def test_filser_logger_id():
    assert_dict_equal(read_igc_headers(['AFIL01460FLIGHT:1']),
                      dict(manufacturer_id='FIL', logger_id='14K'))


def test_date():
    assert_dict_contains_subset(
        dict(date_utc=datetime.date(2012, 8, 15)),
        read_igc_headers(['AFLA6NG', 'HFDTE150812']))


def test_date_only():
    assert_dict_equal(read_igc_headers(['HFDTE150812']),
                      dict(date_utc=datetime.date(2012, 8, 15)))


def test_glider_information():
    assert_dict_contains_subset(
        dict(model='', reg='', cid=''),
        read_igc_headers(['AFLA6NG', 'HFDTE',
                          'HFGTYGLIDERTYPE:',
                          'HFGIDGLIDERID:',
                          'HFCIDCOMPETITIONID:']))

    assert_dict_contains_subset(
        dict(model='HORNET', reg='D_4449', cid='TH'),
        read_igc_headers(['AFLA6NG', 'HFDTE150812',
                          'HFGTYGLIDERTYPE:HORNET',
                          'HFGIDGLIDERID:D_4449',
                          'HFCIDCOMPETITIONID:TH']))


if __name__ == "__main__":
    sys.argv.append(__name__)
    nose.run()
