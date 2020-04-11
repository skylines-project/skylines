import math
from datetime import datetime, timedelta

from flask import Blueprint, request, abort, current_app, make_response

from sqlalchemy import func, literal_column
from sqlalchemy.sql.expression import or_, and_
from sqlalchemy.orm import joinedload, contains_eager, undefer_group
from sqlalchemy.orm.util import aliased
from geoalchemy2.shape import to_shape
from redis.exceptions import ConnectionError

from skylines.api.json import jsonify
from skylines.database import db
from skylines.api.cache import cache
from skylines.api.oauth import oauth
from skylines.lib import files
from skylines.lib.types import is_string
from skylines.lib.table_tools import Pager, Sorter
from skylines.lib.dbutil import get_requested_record
from skylines.lib.datetime import from_seconds_of_day
from skylines.lib.geo import METERS_PER_DEGREE
from skylines.lib.geoid import egm96_height
from skylines.model import (
    User,
    Club,
    Flight,
    Groupflight,
    IGCFile,
    AircraftModel,
    Airport,
    GroupflightComment,
    Notification,
    Event,
    Elevation,
    Location,
)
from skylines.model.notification import create_groupflight_comment_notifications
from skylines.schemas import (
    fields,
    FlightSchema,
    GroupflightSchema,
    GroupflightCommentSchema,
    ContestLegSchema,
    AircraftModelSchema,
    AirportSchema,
    ClubSchema,
    UserSchema,
    Schema,
    ValidationError,
)
from skylines.worker import tasks

import xcsoar
from flights import get_elevations_for_flight, _get_elevations

'''Each individual groupflight uploaded has a groupGroupflightId, Null by default.  
Add groupflight to a group groupflight if another group member submits a groupflight 
with the same igc groupflight plan (md5 hash) within X hours of the last igc groupflight plan submission.
Make sure the other group member's groupflight is also tagged with the groupGroupflightId

Send notification to member when GF_ID'd groupflight has another submission

groupflight.time_modified is normally the upload date'''



###################### -- APIs -- ######################

groupflights_blueprint = Blueprint("groupflights", "skylines")

@groupflights_blueprint.route("/groupflights/all")
@oauth.optional()
def all():
    return _create_list(default_sorting_column="date", default_sorting_order="desc")


@groupflights_blueprint.route("/groupflights/date/<date>")
@oauth.optional()
def date(date):
    try:
        if is_string(date):
            date = datetime.strptime(date, "%Y-%m-%d")

        if isinstance(date, datetime):
            date = date.date()

    except:
        return jsonify(), 404

    return _create_list(
        date=date, default_sorting_column="date", default_sorting_order="desc"
    )


@groupflights_blueprint.route("/groupflights/latest")
@oauth.optional()
def latest():

    #get date of latest group flight.
    query = (
        db.session.query(func.max(Groupflight.time_modified).label("date"))
        .filter(Groupflight.time_modified < datetime.utcnow())
    )

    date_ = query.one().date
    if not date_:
        date_ = datetime.utcnow()

    return date(date_)  #gets list sorted by date


@groupflights_blueprint.route("/groupflights/club/<int:id>")
@oauth.optional()
def club(id):
    club = get_requested_record(Club, id)

    return _create_list(
        club=club, default_sorting_column="date", default_sorting_order="desc"
    )

@groupflights_blueprint.route("/groupflights/airport/<int:id>")
@oauth.optional()
def airport(id):
    airport = get_requested_record(Airport, id)

    return _create_list(
        airport=airport, default_sorting_column="date", default_sorting_order="desc"
    )


@groupflights_blueprint.route("/groupflights/list/<ids>")
@oauth.optional()
def _list(ids):
    if not ids:
        return jsonify(), 400

    try:
        # Split the string into integer IDs
        ids = [int(id) for id in ids.split(",")]
    except ValueError:
        return jsonify(), 404

    return _create_list(
        pinned=ids, default_sorting_column="date", default_sorting_order="desc"
    )


@groupflights_blueprint.route("/groupflights/<groupflight_id>", strict_slashes=False)
@oauth.optional()
def read(groupflight_id):
    groupflight = get_requested_record(Groupflight, groupflight_id)

    # mark_groupflight_notifications_read(groupflight)

    groupflight_json = GroupflightSchema().dump(groupflight).data

    club = get_requested_record(Club, groupflight.club_id)
    club_json = ClubSchema().dump(club).data

    #get list of igcs that belong to groupflight
    ids = db.session.query(Flight.id) \
        .filter(Flight.groupflight_id == groupflight.id) \
        .all()
    ids = [item[0] for item in ids]  #extract integer list

    return jsonify(
        groupflight=groupflight_json, ids=ids, club=club_json
    )


@groupflights_blueprint.route("/groupflights/<flight_id>/json")
@oauth.optional()
def json(flight_id):
    flight = get_requested_record(
        Flight, flight_id, joinedload=(Flight.igc_file, Flight.model)
    )

    current_user = User.get(request.user_id) if request.user_id else None
    if not flight.is_viewable(current_user):
        return jsonify(), 404

    # Return HTTP Status code 304 if an upstream or browser cache already
    # contains the response and if the igc file did not change to reduce
    # latency and server load
    # This implementation is very basic. Sadly Flask (0.10.1) does not have
    # this feature

    last_modified = flight.time_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
    # modified_since = request.headers.get("If-Modified-Since")
    # etag = request.headers.get("If-None-Match")
    # if (modified_since and modified_since == last_modified) or (
    #     etag and etag == flight.igc_file.md5
    # ):
    #     return ("", 304)

    trace = _get_flight_path(flight, threshold=0.0001, max_points=10000)
    if not trace:
        abort(404)

    model = AircraftModelSchema().dump(flight.model).data or None

    resp = make_response(
        jsonify(
            points=trace["points"],
            barogram_t=trace["barogram_t"],
            barogram_h=trace["barogram_h"],
            enl=trace["enl"],
            # contests=trace["contests"],
            elevations_t=trace["elevations_t"],
            elevations_h=trace["elevations_h"],
            sfid=flight.id,
            geoid=trace["geoid"],
            additional=dict(
                registration=flight.registration,
                competition_id=flight.competition_id,
                model=model,
                score=flight.index_score,
                distance=flight.olc_classic_distance,
                triangleDistance=flight.olc_triangle_distance,
            ),
        )
    )

    resp.headers["Last-Modified"] = last_modified
    resp.headers["Etag"] = flight.igc_file.md5
    return resp



@groupflights_blueprint.route("/groupflights/<groupflight_id>/comments", methods=("POST",))
@oauth.required()
def add_comment(groupflight_id):
    groupflight = get_requested_record(Groupflight, groupflight_id, club)

    current_user = User.get(request.user_id)
    if not current_user:
        return jsonify(), 403

    json = request.get_json()
    if json is None:
        return jsonify(error="invalid-request"), 400

    try:
        data = GroupflightCommentSchema().load(json).data
    except ValidationError as e:
        return jsonify(error="validation-failed", fields=e.messages), 422

    comment = GroupflightComment()
    comment.user = current_user
    comment.groupflight = groupflight
    comment.text = data["text"]

    create_groupflight_comment_notifications(comment)

    db.session.commit()

    return jsonify()


################  functions  ##################

def groupflight_actions(flightCurrent, igc_file):
    '''Finds igc files within 12 hrs of the last uploaded igc with a matching flight plan '''

    latest = db.session.query(Flight.id) \
        .filter(Flight.club_id != None) \
        .filter(Flight.club_id == flightCurrent.club_id) \
        .filter(Flight.flight_plan_md5 == igc_file.flight_plan_md5) \
        .filter(Flight.date_local == flightCurrent.date_local)  # \
        # .filter(Flight.time_modified + timedelta(hours=12) >= datetime.utcnow()).all()

    latest = latest.all()
    if len(latest) > 1:  # igc should be part of group flight
        alreadyGrouped = db.session.query(Flight.id) \
            .filter(Flight.club_id == flightCurrent.club_id) \
            .filter(Flight.flight_plan_md5 == igc_file.flight_plan_md5) \
            .filter(Flight.groupflight_id != None).all()

        if len(alreadyGrouped) > 0:  # add to this group flight
            gfid = db.session.query(Flight.groupflight_id).filter(Flight.id == alreadyGrouped[0][0]).all()[0][0]  # get from first entry
            groupflight = db.session.query(Groupflight).filter(Groupflight.id == gfid)
            groupflight.time_modified = datetime.utcnow()
            for flight_id in latest:
                flight = Flight.get(flight_id)
                flight.groupflight_id = gfid
        else:  # create group flight
            groupflight = Groupflight()
            groupflight.landscape = igc_file.landscape
            groupflight.flight_plan_md5 = igc_file.flight_plan_md5
            groupflight.time_created = datetime.utcnow()
            groupflight.time_modified = datetime.utcnow()
            groupflight.date_flight = flightCurrent.date_local
            groupflight.club_id = flightCurrent.club_id
            if flightCurrent.takeoff_airport_id != None:
                groupflight.takeoff_airport_id = flightCurrent.takeoff_airport.id
            db.session.add(groupflight)
            db.session.flush()
            for flight_id in latest:
                flight = Flight.get(flight_id)
                flight.groupflight_id = groupflight.id
        #db.session.commit()
        return


def mark_groupflight_notifications_read(groupflight):
    if not request.user_id:
        return

    def add_groupflight_filter(query):
        return query.filter(Event.groupflight_id == groupflight.id)

    Notification.mark_all_read(User.get(request.user_id), filter_func=add_groupflight_filter)
    db.session.commit()

def _create_list(
    created=None,
    time=None,
    date=None,
    club=None,
    landscape=None,
    airport=None,
    pinned=None,
    filter=None,
    default_sorting_column = "date",
    default_sorting_order = "desc"

):

    subq = (
        db.session.query(GroupflightComment.groupflight_id, func.count("*").label("count"))
        .group_by(GroupflightComment.groupflight_id)
        .subquery()
    )

    groupflights = (
        db.session.query(Groupflight, subq.c.count)
        .outerjoin(Groupflight.club)
        .options(contains_eager(Groupflight.club))
        .outerjoin(Groupflight.takeoff_airport)
        .options(contains_eager(Groupflight.takeoff_airport))
        .outerjoin((subq, Groupflight.comments))
    )

    if time:
        groupflights = groupflights.filter(Groupflight.time_modified == time)

    if date:
        groupflights = groupflights.filter(Groupflight.date_flight == date)

    if club:
        groupflights = groupflights.filter(Groupflight.club == club)

    if landscape:
        groupflights.filter(Groupflight.landscape == landscape)

    if airport:
        groupflights = groupflights.filter(Groupflight.takeoff_airport == airport)

    if pinned:
        groupflights = groupflights.filter(Groupflight.id.in_(pinned))

    if filter is not None:
        groupflights = groupflights.filter(filter)

    valid_columns = {
        "created": getattr(Groupflight, "time_created"),
        "date": getattr(Groupflight, "date_flight"),
        "time": getattr(Groupflight, "time_modified"),
        "landscape": getattr(Groupflight, "landscape"),
        "airport": getattr(Airport, "name"),
        "club": getattr(Club, "name"),
    }

    groupflights_count = groupflights.count()

    groupflights = Sorter.sort(
        groupflights,
        "groupflights",
        default_sorting_column,
        valid_columns=valid_columns,
        default_order=default_sorting_order,
    )

    groupflights = Pager.paginate(
        groupflights,
        "groupflights",
        items_per_page=int(current_app.config.get("SKYLINES_LISTS_DISPLAY_LENGTH", 50)),
    )

    groupflight_schema = GroupflightSchema()
    groupflights_json = []
    for f, num_comments in groupflights:
        groupflight = groupflight_schema.dump(f).data
        groupflight["numComments"] = num_comments
        groupflights_json.append(groupflight)

    json = dict(groupflights=groupflights_json, count=groupflights_count)

    if time: json["time"] = date.isoformat()

    if date:
        json["date"] = date.isoformat()

    if created:
        json["created"] = date.isoformat()

    if club:
        club_schema = ClubSchema(only=("id", "name"))
        json["club"] = club_schema.dump(club).data

    if airport:
        airport_schema = AirportSchema(only=("id", "name", "countryCode"))
        json["airport"] = airport_schema.dump(airport).data

    return jsonify(json)


def mark_user_notifications_read(pilot):
    if not request.user_id:
        return

    def add_groupflight_filter(query):
        return query.filter(Event.actor_id == pilot.id)

    Notification.mark_all_read(User.get(request.user_id), filter_func=add_groupflight_filter)
    db.session.commit()

def _get_flight_path(flight, threshold=0.001, max_points=3000):
    '''This version excludes contest_traces from group display'''
    num_levels = 4
    zoom_factor = 4
    zoom_levels = [0]
    zoom_levels.extend(
        [
            round(
                -math.log(
                    32.0 / 45.0 * (threshold * pow(zoom_factor, num_levels - i - 1)), 2
                )
            )
            for i in range(1, num_levels)
        ]
    )

    xcsoar_flight = xcsoar.Flight(files.filename_to_path(flight.igc_file.filename))

    if flight.qnh:
        xcsoar_flight.setQNH(flight.qnh)

    begin = flight.takeoff_time - timedelta(seconds=2 * 60)
    end = flight.landing_time + timedelta(seconds=2 * 60)

    if begin > end:
        begin = datetime.min
        end = datetime.max

    xcsoar_flight.reduce(
        begin=begin,
        end=end,
        num_levels=num_levels,
        zoom_factor=zoom_factor,
        threshold=threshold,
        max_points=max_points,
    )

    encoded_flight = xcsoar_flight.encode()

    points = encoded_flight["locations"]
    barogram_t = encoded_flight["times"]
    barogram_h = encoded_flight["altitude"]
    enl = encoded_flight["enl"]

    elevations_t, elevations_h = _get_elevations(flight)
    # contest_traces = _get_contest_traces(flight)

    geoid_height = (
        egm96_height(flight.takeoff_location) if flight.takeoff_location else 0
    )

    return dict(
        points=points,
        barogram_t=barogram_t,
        barogram_h=barogram_h,
        enl=enl,
        # contests=contest_traces,
        elevations_t=elevations_t,
        elevations_h=elevations_h,
        sfid=flight.id,
        geoid=geoid_height,
    )


