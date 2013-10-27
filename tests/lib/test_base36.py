# -*- coding: utf-8 -*-

import sys
import nose
from nose.tools import eq_

from skylines.lib import base36


def test_encoding():
    eq_(base36.encode(0), '0')
    eq_(base36.encode(1), '1')
    eq_(base36.encode(9), '9')
    eq_(base36.encode(10), 'A')
    eq_(base36.encode(11), 'B')
    eq_(base36.encode(35), 'Z')
    eq_(base36.encode(36), '10')
    eq_(base36.encode(36 + 10), '1A')
    eq_(base36.encode(36 * 10), 'A0')
    eq_(base36.encode(36 * 36), '100')


def test_decoding():
    eq_(base36.decode('0'), 0)
    eq_(base36.decode('1'), 1)
    eq_(base36.decode('9'), 9)
    eq_(base36.decode('A'), 10)
    eq_(base36.decode('B'), 11)
    eq_(base36.decode('Z'), 35)
    eq_(base36.decode('10'), 36)
    eq_(base36.decode('1A'), 36 + 10)
    eq_(base36.decode('A0'), 36 * 10)
    eq_(base36.decode('100'), 36 * 36)


if __name__ == "__main__":
    sys.argv.append(__name__)
    nose.run()
