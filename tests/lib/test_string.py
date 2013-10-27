# -*- coding: utf-8 -*-

import sys
import nose
from nose.tools import eq_, assert_raises

from skylines.lib.string import normalize_whitespace, import_ascii, \
    import_alnum


def test_normalize_whitespace():
    eq_(normalize_whitespace('abc def'), 'abc def')
    eq_(normalize_whitespace(u'abc def'), u'abc def')

    eq_(normalize_whitespace('  abc def  '), 'abc def')
    eq_(normalize_whitespace(u'  abc def  '), u'abc def')

    eq_(normalize_whitespace('abc   def'), 'abc   def')
    eq_(normalize_whitespace(u'abc   def'), u'abc   def')

    eq_(normalize_whitespace('abc\ndef'), 'abc def')
    eq_(normalize_whitespace(u'abc\ndef'), u'abc def')

    eq_(normalize_whitespace('abc \r\ndef  '), 'abc   def')
    eq_(normalize_whitespace(u'abc \r\ndef  '), u'abc   def')

    assert_raises(AssertionError, normalize_whitespace, None)
    assert_raises(AssertionError, normalize_whitespace, 5)
    assert_raises(AssertionError, normalize_whitespace, [])


def test_import_ascii():
    eq_(import_ascii('abc def'), u'abc def')
    eq_(import_ascii('abc äöü def'), u'abc  def')
    eq_(import_ascii('abc +-. def'), u'abc +-. def')

    assert_raises(AssertionError, import_ascii, u'abc def')
    assert_raises(AssertionError, import_ascii, None)


def test_import_alnum():
    eq_(import_alnum('abc def'), u'abcdef')
    eq_(import_alnum('abc +-. def'), u'abcdef')

    assert_raises(AssertionError, import_alnum, u'abc def')
    assert_raises(AssertionError, import_alnum, None)


if __name__ == "__main__":
    sys.argv.append(__name__)
    nose.run()
