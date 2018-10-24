# -*- coding: utf-8 -*-

import pytest

from skylines.lib import files
from skylines.lib.types import is_unicode


@pytest.mark.parametrize(
    "input,expected",
    [
        (b"foo/bar/baz.igc", u"baz.igc"),
        (u"HERR.müller@123.igc", u"herr.m_ller_123.igc"),
        (u"abc/...1234.igc", u"1234.igc"),
        (u"", u"empty"),
    ],
)
def test_sanitise_filename(input, expected):
    output = files.sanitise_filename(input)

    assert is_unicode(output)
    assert output == expected
