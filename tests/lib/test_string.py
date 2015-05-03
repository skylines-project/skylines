# -*- coding: utf-8 -*-

import pytest

from skylines.lib.string import normalize_whitespace, import_ascii, \
    import_alnum


def test_normalize_whitespace():
    assert normalize_whitespace('abc def'), 'abc def'
    assert normalize_whitespace(u'abc def'), u'abc def'

    assert normalize_whitespace('  abc def  '), 'abc def'
    assert normalize_whitespace(u'  abc def  '), u'abc def'

    assert normalize_whitespace('abc   def'), 'abc   def'
    assert normalize_whitespace(u'abc   def'), u'abc   def'

    assert normalize_whitespace('abc\ndef'), 'abc def'
    assert normalize_whitespace(u'abc\ndef'), u'abc def'

    assert normalize_whitespace('abc \r\ndef  '), 'abc   def'
    assert normalize_whitespace(u'abc \r\ndef  '), u'abc   def'

    with pytest.raises(AssertionError): normalize_whitespace(None)
    with pytest.raises(AssertionError): normalize_whitespace(5)
    with pytest.raises(AssertionError): normalize_whitespace([])


def test_import_ascii():
    assert import_ascii('abc def'), u'abc def'
    assert import_ascii('abc äöü def'), u'abc  def'
    assert import_ascii('abc +-. def'), u'abc +-. def'

    with pytest.raises(AssertionError): import_ascii(u'abc def')
    with pytest.raises(AssertionError): import_ascii(None)


def test_import_alnum():
    assert import_alnum('abc def'), u'abcdef'
    assert import_alnum('abc +-. def'), u'abcdef'

    with pytest.raises(AssertionError): import_alnum(u'abc def')
    with pytest.raises(AssertionError): import_alnum(None)
