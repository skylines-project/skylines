import re


whitespace_re = re.compile(r'[\x00-\x20\s]')
non_alnum_re = re.compile(r'[^0-9a-zA-Z]')


def normalize_whitespace(s):
    """Strip the string and replace all whitespace sequences and other
    non-printable characters with a single space."""

    assert isinstance(s, str) or isinstance(s, unicode)

    return whitespace_re.sub(' ', s.strip())


def import_ascii(s):
    """Import a 'str' object, convert to a 'unicode' object, discarding all
    non-ASCII characters."""

    assert isinstance(s, str)

    s = normalize_whitespace(s)
    return unicode(s, 'ascii', 'ignore')


def import_alnum(s):
    """Import a 'str' object, convert to a 'unicode' object,
    discarding all non-alphanumeric characters (ASCII only)."""

    assert isinstance(s, str)

    s = non_alnum_re.sub('', s)
    return unicode(s, 'ascii')


def isnumeric(s):
    """Check if a string can be parsed as floating point value"""
    try:
        float(s)
    except ValueError:
        return False

    return True
