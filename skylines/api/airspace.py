from skylines.api.schemas import airspace_list_schema
from skylines.model import Airspace


def get_airspaces_by_location(location):
    return airspace_list_schema.dump(Airspace.by_location(location).all(), many=True).data
