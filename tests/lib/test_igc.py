# -*- coding: utf-8 -*-

import datetime
from skylines.lib.igc import read_igc_headers


def test_empty_file():
    assert read_igc_headers([]) == {}


def test_logger_information():
    assert (read_igc_headers(['AFLA6NG']) ==
            dict(manufacturer_id='FLA', logger_id='6NG'))


def test_filser_logger_id():
    assert (read_igc_headers(['AFIL01460FLIGHT:1']) ==
            dict(manufacturer_id='FIL', logger_id='14K'))


def test_date():
    headers = read_igc_headers(['AFLA6NG', 'HFDTE150812'])

    assert 'date_utc' in headers
    assert headers['date_utc'] == datetime.date(2012, 8, 15)


def test_date_only():
    assert (read_igc_headers(['HFDTE150812']) ==
            dict(date_utc=datetime.date(2012, 8, 15)))


def test_glider_information():
    headers = read_igc_headers([
        'AFLA6NG',
        'HFDTE',
        'HFGTYGLIDERTYPE:',
        'HFGIDGLIDERID:',
        'HFCIDCOMPETITIONID:'
    ])

    assert 'model' in headers
    assert headers['model'] == ''

    assert 'reg' in headers
    assert headers['reg'] == ''

    assert 'cid' in headers
    assert headers['cid'] == ''

    headers = read_igc_headers([
        'AFLA6NG',
        'HFDTE150812',
        'HFGTYGLIDERTYPE:HORNET',
        'HFGIDGLIDERID:D_4449',
        'HFCIDCOMPETITIONID:TH'
    ])

    assert 'model' in headers
    assert headers['model'] == 'HORNET'

    assert 'reg' in headers
    assert headers['reg'] == 'D_4449'

    assert 'cid' in headers
    assert headers['cid'] == 'TH'
