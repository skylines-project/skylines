# -*- coding: utf-8 -*-

from skylines.lib import base36


def test_encoding():
    assert base36.encode(0) == '0'
    assert base36.encode(1) == '1'
    assert base36.encode(9) == '9'
    assert base36.encode(10) == 'A'
    assert base36.encode(11) == 'B'
    assert base36.encode(35) == 'Z'
    assert base36.encode(36) == '10'
    assert base36.encode(36 + 10) == '1A'
    assert base36.encode(36 * 10) == 'A0'
    assert base36.encode(36 * 36) == '100'


def test_decoding():
    assert base36.decode('0') == 0
    assert base36.decode('1') == 1
    assert base36.decode('9') == 9
    assert base36.decode('A') == 10
    assert base36.decode('B') == 11
    assert base36.decode('Z') == 35
    assert base36.decode('10') == 36
    assert base36.decode('1A') == 36 + 10
    assert base36.decode('A0') == 36 * 10
    assert base36.decode('100') == 36 * 36
