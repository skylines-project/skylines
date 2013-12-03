from skylines.model import Airspace, Location


def get_airspaces_by_location(location):
    if not isinstance(location, Location):
        raise TypeError('Invalid `location` parameter.')

    airspaces = Airspace.by_location(location)
    return map(airspace_to_dict, airspaces)


def airspace_to_dict(airspace):
    return {
        'name': airspace.name,
        'base': airspace.base,
        'top': airspace.top,
        'airspace_class': airspace.airspace_class,
        'country': airspace.country_code,
    }
