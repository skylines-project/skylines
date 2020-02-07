from flask import Blueprint, request, g
from sqlalchemy import func
from datetime import datetime, timedelta
from skylines.api.json import jsonify
from skylines.database import db
from skylines.api.oauth import oauth
from skylines.lib.dbutil import get_requested_record
from skylines.model import Club, User, Flight, GroupFlight
from skylines.model.notification import create_club_join_event

from skylines.schemas import GroupFlightSchema, ValidationError


'''Each individual flight uploaded has a groupFlightId, Null by default.  
Add flight to a group flight if another group member submits a flight 
with the same igc flight plan (md5 hash) within X hours of the last igc flight plan submission.
Make sure the other group member's flight is also tagged with the groupFlightId

Send notification to member when GF_ID'd flight has another submission

flight.time_modified is normally the upload date'''

# groupFlights_blueprint = Blueprint("group_flights", "skylines")
#
# @groupFlights_blueprint("/group_flights", strict_slashes=False)
# def _list():
# # List group flights by date
# #     data = _handle_request_flight_group("club_id")
#
#     group_flight_schema = GroupFlightSchema(only=("id", "clubid", "md5","takeoffAirport", "timeCreated"))
#     club_info = []
#     for club, count, flights, users in data["result"]: #"count" needs to be here
#         row = {"club": club_schema.dump(club).data,
#                "flights": flights,
#                "users": users,
#                "email": club.email_address,
#                "website": club.website
#         }
#
#         club_info.append({"group-flights": group_flight_schema.dump})
#
#     return jsonify(club_info=club_info, total=g.paginators["result"].count)

def group_flight_actions(flightCurrent, igc_file):
    '''Finds igc files within 24 hrs of the last uploaded igc with a matching flight plan '''
    print 'testbch'
    latest =  db.session.query(Flight.id)\
            .filter(Flight.club_id == flightCurrent.club_id)\
            .filter(Flight.flight_plan_md5 == igc_file.flight_plan_md5)\
            .filter(Flight.time_modified + timedelta(hours=24) >= datetime.utcnow()).all()

    if len(latest) > 1: # igc is part of group flight
        alreadyGrouped = db.session.query(Flight.id)\
                .filter(Flight.club_id == flightCurrent.club_id)\
                .filter(Flight.flight_plan_md5 == igc_file.flight_plan_md5)\
                .filter(Flight.group_flight_id != None).all()

        if len(alreadyGrouped) > 0: #add to this group flight
            gfid = Flight.query(Flight.group_flight_id).filter(Flight.id == alreadyGrouped[0])[0] #get from first entry
            for flight_id in latest:
                flight = Flight.get(flight_id)
                flight.group_flight_id = gfid
        else: # create group flight
            group_flight = GroupFlight()
            group_flight.flight_plan_md5 = igc_file.flight_plan_md5
            group_flight.time_created = datetime.utcnow()
            group_flight.time_modified = datetime.utcnow()
            group_flight.club_id = flightCurrent.club_id
            if flightCurrent.takeoff_airport != None:
                group_flight.takeoff_airport = flightCurrent.takeoff_airport.name
            db.session.add(group_flight)
        db.session.commit()









