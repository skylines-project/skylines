from skylines.api.schemas import airport_schema, airport_list_schema
from skylines.model import Airport, Bounds


def get_airports_by_bbox(bbox):
    if not isinstance(bbox, Bounds):
        raise TypeError('Invalid `bbox` parameter.')

    bbox.normalize()
    if bbox.get_size() > 20 * 20:
        raise ValueError('Requested `bbox` is too large.')

    data, errors = airport_list_schema.dump(Airport.by_bbox(bbox), many=True)
    return data


def get_airport(id):
    airport = Airport.get(id)
    if not airport:
        raise KeyError('The requested airport was not found.')

    data, errors = airport_schema.dump(airport)
    return data
