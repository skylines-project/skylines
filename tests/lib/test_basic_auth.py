# -*- coding: utf-8 -*-

from skylines.lib.basic_auth import encode
from skylines.lib.types import is_unicode


def test_unicode():
    result = encode(u"foo", u"bar")
    assert result == u"Basic Zm9vOmJhcg=="
    assert is_unicode(result)


def test_bytes():
    result = encode("foo", "bar")
    assert result == u"Basic Zm9vOmJhcg=="
    assert is_unicode(result)
