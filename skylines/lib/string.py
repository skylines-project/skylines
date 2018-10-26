# flake8: noqa F821

import re
import sys

from skylines.lib.types import is_bytes


whitespace_re = re.compile(br"[\x00-\x20\s]")
non_alnum_re = re.compile(br"[^0-9a-zA-Z]")


def normalize_whitespace(s):
    """Strip the string and replace all whitespace sequences and other
    non-printable characters with a single space."""

    assert is_bytes(s)

    return whitespace_re.sub(b" ", s.strip())


def import_ascii(s):
    """Import a byte string, convert to a unicode string, discarding all
    non-ASCII characters."""

    assert is_bytes(s)

    s = normalize_whitespace(s)
    return s.decode("ascii", "ignore")


def import_alnum(s):
    """Import a byte string, convert to a unicode string,
    discarding all non-alphanumeric characters (ASCII only)."""

    assert is_bytes(s)

    s = non_alnum_re.sub(b"", s)
    return s.decode("ascii")


def isnumeric(s):
    """Check if a string can be parsed as floating point value"""
    try:
        float(s)
    except ValueError:
        return False

    return True


def unicode_to_str(value):
    if sys.version_info[0] == 2:
        return value.encode("utf-8")
    else:
        return value


def str_to_unicode(value):
    if sys.version_info[0] == 2:
        return value.decode("utf-8")
    else:
        return value


def to_unicode(value):
    if sys.version_info[0] == 2:
        return unicode(value)
    else:
        return str(value)
