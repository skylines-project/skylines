from flask import abort
from skylines.model import Location


def parse_location(args):
    try:
        latitude = float(args['lat'])
        longitude = float(args['lon'])
        return Location(latitude=latitude, longitude=longitude)

    except (KeyError, ValueError):
        abort(400)
