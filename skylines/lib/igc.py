# -*- coding: utf-8 -*-

import re
from skylines.lib import files
from skylines.lib.base36 import base36encode
from skylines.lib.string import import_ascii, import_alnum

hfgid_re = re.compile(r'HFGID\s*GLIDER\s*ID\s*:(.*)', re.IGNORECASE)
hfgty_re = re.compile(r'HFGTY\s*GLIDER\s*TYPE\s*:(.*)', re.IGNORECASE)
hfcid_re = re.compile(r'HFCID.*:(.*)', re.IGNORECASE)
afil_re = re.compile(r'AFIL(\d*)FLIGHT', re.IGNORECASE)


def read_igc_headers(filename):
    path = files.filename_to_path(filename)

    try:
        f = file(path, 'r')
    except IOError:
        return None

    igc_headers = dict()

    for i, line in enumerate(f):
        if line[0] == 'A' and len(line) >= 4:
            igc_headers['manufacturer_id'] = line[1:4]

            if len(line) >= 7:
                igc_headers['logger_id'] = parse_logger_id(line)

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
            return base36encode(int(match.group(1)))
    else:
        return import_alnum(line[4:7]).upper()


def parse_pattern(pattern, line):
    match = pattern.match(line)

    if not match:
        return None

    return import_ascii(match.group(1))
