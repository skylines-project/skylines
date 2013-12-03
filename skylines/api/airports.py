from skylines.model import Airport, Bounds


def get_airports_by_bbox(bbox):
    if not isinstance(bbox, Bounds):
        raise TypeError('Invalid `bbox` parameter.')

    bbox.normalize()
    if bbox.get_size() > 20 * 20:
        raise ValueError('Requested `bbox` is too large.')

    return map(airport_to_dict, Airport.by_bbox(bbox))


def get_airport(id):
    airport = Airport.get(id)
    if not airport:
        raise KeyError('The requested airport was not found.')

    return airport_to_dict(airport, short=False)


def airport_to_dict(airport, short=True):
    result = {
        'id': airport.id,
        'name': airport.name,
        'elevation': airport.altitude,
        'location': {
            'latitude': airport.location.latitude,
            'longitude': airport.location.longitude,
        },
    }

    if not short:
        result.update({
            'icao': airport.icao,
            'short_name': airport.short_name,
            'country_code': airport.country_code,
            'type': airport.type,
            'runways': [{
                'length': airport.runway_len,
                'direction': airport.runway_dir,
                'surface': airport.surface,
            }],
            'frequencies': [{
                'frequency': airport.frequency,
            }],
        })

    return result
