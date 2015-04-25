# -*- coding: utf-8 -*-

from __future__ import absolute_import

import re
from datetime import datetime

from . import base36
from .string import import_ascii, import_alnum

hfdte_re = re.compile(r'HFDTE(\d{6})', re.IGNORECASE)
hfgid_re = re.compile(r'HFGID\s*GLIDER\s*ID\s*:(.*)', re.IGNORECASE)
hfgty_re = re.compile(r'HFGTY\s*GLIDER\s*TYPE\s*:(.*)', re.IGNORECASE)
hfcid_re = re.compile(r'HFCID.*:(.*)', re.IGNORECASE)
afil_re = re.compile(r'AFIL(\d*)FLIGHT', re.IGNORECASE)


def read_igc_headers(f):
    """ Read IGC file headers from a file-like object, a list of strings or a
    file if the parameter is a path. """

    if isinstance(f, str) or isinstance(f, unicode):
        try:
            f = file(f, 'r')
        except IOError:
            return None

    igc_headers = dict()

    for i, line in enumerate(f):
        if line[0] == 'A':
            length = len(line)

            if length >= 4:
                igc_headers['manufacturer_id'] = line[1:4]

            if length >= 7:
                igc_headers['logger_id'] = parse_logger_id(line)

        if line.startswith('HFDTE'):
            igc_headers['date_utc'] = parse_date(line)

        if line.startswith('HFGTY'):
            igc_headers['model'] = parse_pattern(hfgty_re, line)

        if line.startswith('HFGID'):
            igc_headers['reg'] = parse_pattern(hfgid_re, line)

        if line.startswith('HFCID'):
            igc_headers['cid'] = parse_pattern(hfcid_re, line)

        # don't read more than 100 lines, that should be enough
        if i > 100:
            break

    return igc_headers


def parse_logger_id(line):
    # non IGC loggers may use more than 3 characters as unique ID.
    # we just use the first three, currently no model is known which
    # really uses more than 3 characters.

    if line[1:4] == 'FIL':
        # filser doesn't respect the IGC file specification and
        # stores the unique id as base 10 instead of base 36.
        match = afil_re.match(line)
        if match and match.group(1):
            return base36.encode(int(match.group(1)))
    else:
        return import_alnum(line[4:7]).upper()


def parse_pattern(pattern, line):
    match = pattern.match(line)

    if not match:
        return None

    return import_ascii(match.group(1))


def parse_date(line):
    match = hfdte_re.match(line)

    if not match:
        return None

    date_str = match.group(1)
    try:
        return datetime.strptime(date_str, '%d%m%y').date()
    except ValueError:
        return None
