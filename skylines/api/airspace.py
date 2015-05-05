from skylines.api.schemas import airspace_list_schema
from skylines.model import Airspace, Location


def get_airspaces_by_location(location):
    if not isinstance(location, Location):
        raise TypeError('Invalid `location` parameter.')

    data, errors = airspace_list_schema.dump(
        Airspace.by_location(location).all(), many=True)

    return data
