from flask import abort
from webargs import fields

from skylines.model import Location


pagination_args = {
    'page': fields.Integer(missing=1, location='query', validate=lambda val: val > 0),
    'per_page': fields.Integer(missing=30, location='query', validate=lambda val: val <= 100),
}


def parse_location(args):
    try:
        latitude = float(args['lat'])
        longitude = float(args['lon'])
        return Location(latitude=latitude, longitude=longitude)

    except (KeyError, ValueError):
        abort(400)
