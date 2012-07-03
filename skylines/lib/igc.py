# -*- coding: utf-8 -*-

import re
from sqlalchemy import func
from sqlalchemy.sql.expression import and_, desc
from skylines import files
from skylines.model import DBSession, Model, Flight

hfgid_re = re.compile(r'HFGID\s*GLIDER\s*ID\s*:(.*)', re.IGNORECASE)
hfgty_re = re.compile(r'HFGTY\s*GLIDER\s*TYPE\s*:(.*)', re.IGNORECASE)
afil_re = re.compile(r'AFIL(\d*)FLIGHT', re.IGNORECASE)


def read_igc_header(igc_file):
    path = files.filename_to_path(igc_file.filename)

    try:
        f = file(path, 'r')
    except IOError:
        return dict()

    igc_headers = dict()

    i = 0
    for line in f:
        if line[0] == 'A' and len(line) >= 4:
            igc_headers['manufacturer_id'] = line[1:4]

            if len(line) >= 7:
                igc_headers['logger_id'] = parse_logger_id(line)

        if line.startswith('HFGTY'):
            igc_headers['model'] = parse_glider_type(line)

        if line.startswith('HFGID'):
            igc_headers['reg'] = parse_glider_reg(line)

        # don't read more than 100 lines, that should be enough
        i += 1
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
        return line[4:7]


def parse_glider_type(line):
    match = hfgty_re.match(line)

    if not match:
        return None

    return match.group(1).strip()


def parse_glider_reg(line):
    match = hfgid_re.match(line)

    if not match:
        return None

    return match.group(1).strip()


def guess_model(igc_file):
    # first try to find the reg number in the database
    if igc_file.registration is not None:
        glider_reg = igc_file.registration

        result = DBSession.query(Flight) \
            .filter(func.upper(Flight.registration) == func.upper(glider_reg)) \
            .order_by(desc(Flight.id)) \
            .first()

        if result and result.model_id:
            return result.model_id

    if igc_file.model is not None:
        glider_type = igc_file.model.lower()

        # otherwise, try to guess the glider model by the glider type igc header
        text_fragments = ['%{}%'.format(v) for v in re.sub(r'[^a-z]', ' ', glider_type).split()]
        digit_fragments = ['%{}%'.format(v) for v in re.sub(r'[^0-9]', ' ', glider_type).split()]

        if not text_fragments and not digit_fragments:
            return None

        glider_type_clean = re.sub(r'[^a-z0-9]', '', glider_type)

        result = DBSession.query(Model) \
            .filter(and_( \
                func.regexp_replace(func.lower(Model.name), '[^a-z]', ' ').like(func.any(text_fragments)), \
                func.regexp_replace(func.lower(Model.name), '[^0-9]', ' ').like(func.all(digit_fragments)))) \
            .order_by(func.levenshtein(func.regexp_replace(func.lower(Model.name), '[^a-z0-9]', ''), glider_type_clean))

        if result.first():
            return result.first().id

    # nothing found
    return None


# base 36 encoding/decoding taken from wikipedia sample code
# http://en.wikipedia.org/wiki/Base_36#Python_Conversion_Code
def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')

    if number >= 0 and number <= 9:
        return alphabet[number]

    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36


def base36decode(number):
    return int(number, 36)
