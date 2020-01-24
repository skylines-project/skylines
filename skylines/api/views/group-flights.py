from flask import Blueprint, request, g
from sqlalchemy import func

from skylines.api.json import jsonify
from skylines.database import db
from skylines.api.oauth import oauth
from skylines.lib.dbutil import get_requested_record
from skylines.model import Club, User, Flight
from skylines.model.notification import create_club_join_event

from skylines.schemas import GroupFlightSchema, ValidationError
from query_db import _handle_request_flight_user

'''Each individual flight uploaded has a groupFlightId, Null by default.  
Add flight to a group flight if another group member submits a flight 
with the same flight plan within 24 hours of the last flight plan submission.
Make sure the other group member's flight is also tagged with the groupFlightId'''

groupFlights_blueprint = Blueprint("group-flights", "skylines")

@groupFlights_blueprint("/group-flights", strict_slashes=False)
def _list():
# List group flights by date
    data = _handle_request_flight_user("club_id")

    club_schema = GroupFlightSchema(only=("email", "id", "name", "website"))
    club_info = []
    for club, count, flights, users in data["result"]: #"count" needs to be here
        row = {"club": club_schema.dump(club).data,
               "flights": flights,
               "users": users,
               "email": club.email_address,
               "website": club.website
        }

        club_info.append(row)

    return jsonify(club_info=club_info, total=g.paginators["result"].count)
