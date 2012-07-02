# -*- coding: utf-8 -*-

import re
from sqlalchemy import func
from sqlalchemy.sql.expression import and_, desc
from skylines import files
from skylines.model import DBSession, Model, Flight

def read_igc_header(igc_file):
    path = files.filename_to_path(igc_file.filename)

    try:
        f = file(path, 'r')
    except IOError:
        return

    igc_headers = dict()

    i = 0
    for line in f:
        if line[0] == 'A' and len(line) >= 4:
            igc_headers['manufacturer_id'] = line[1:4]

        if line.startswith('HFGTY'):
            igc_headers['model'] = parse_glider_type(line)

        if line.startswith('HFGID'):
            igc_headers['reg'] = parse_glider_reg(line)

        # don't read more than 100 lines, that should be enough
        i += 1
        if i > 100:
            break

    return igc_headers

def parse_glider_type(line):
    hfgty_re = re.compile(r'HFGTY\s*GLIDER\s*TYPE\s*:(.*)', re.IGNORECASE)
    match = hfgty_re.match(line)

    if not match:
        return None

    return match.group(1).lower().strip()

def parse_glider_reg(line):
    hfgid_re = re.compile(r'HFGID\s*GLIDER\s*ID\s*:(.*)', re.IGNORECASE)
    match = hfgid_re.match(line)

    if not match:
        return None

    return match.group(1).strip()

def guess_model(igc_headers):
    # first try to find the reg number in the database
    if igc_headers.get('reg') is not None:
        glider_reg = igc_headers.get('reg')

        result = DBSession.query(Flight) \
            .filter(func.upper(Flight.registration) == func.upper(glider_reg)) \
            .order_by(desc(Flight.id)) \
            .first()

        if result and result.model_id:
            return result.model_id

    if igc_headers.get('model') is not None:
        glider_type = igc_headers.get('model')

        # otherwise, try to guess the glider model by the glider type igc header
        text_fragments = ['%{}%'.format(v) for v in re.sub(r'[^a-z]', ' ', glider_type).split()]
        digit_fragments = ['%{}%'.format(v) for v in re.sub(r'[^0-9]', ' ', glider_type).split()]

        glider_type_clean = re.sub(r'[^a-z0-9]', '', glider_type)

        if not text_fragments and not digit_fragments:
            return None

        result = DBSession.query(Model) \
            .filter(and_( \
                func.regexp_replace(func.lower(Model.name), '[^a-z]', ' ').like(func.any(text_fragments)), \
                func.regexp_replace(func.lower(Model.name), '[^0-9]', ' ').like(func.all(digit_fragments)) )) \
            .order_by(func.levenshtein(func.regexp_replace(func.lower(Model.name), '[^a-z0-9]', ''), glider_type_clean))

        if result.first():
            return result.first().id

    # nothing found
    return None
