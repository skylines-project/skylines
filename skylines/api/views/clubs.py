from flask import Blueprint, request, g
from sqlalchemy import func

from skylines.api.json import jsonify
from skylines.database import db
from skylines.api.oauth import oauth
from skylines.lib.dbutil import get_requested_record
from skylines.model import Club, User, Flight
from skylines.model.notification import create_club_join_event

from skylines.schemas import ClubSchema, ValidationError
from query_db import _handle_request_flight_user_byClub

clubs_blueprint = Blueprint("clubs", "skylines")

@clubs_blueprint.route("/clubs/choose-club", strict_slashes=False) #make a dummy route
def _listClubsByName():
    clubs = Club.query().order_by(func.lower(Club.name))

    name_filter = request.args.get("name")
    if name_filter:
        clubs = clubs.filter_by(name=name_filter)

    return jsonify(clubs=ClubSchema(only=("id", "name")).dump(clubs, many=True).data)

@clubs_blueprint.route("/clubs", strict_slashes=False)
def _listInfo():
# List clubs with info
    data = _handle_request_flight_user_byClub()

    club_schema = ClubSchema(only=("email", "id", "name", "website"))
    club_info = []
    if len(data["result"].all())>0:
        for club, flights, users, rank in data["result"]:
            row = {"club": club_schema.dump(club).data,
                   "flights": flights,
                   "users": users,
                   "email": club.email_address,
                   "website": club.website
            }
            club_info.append(row)
    return jsonify(club_info=club_info, total=g.paginators["result"].count)


@clubs_blueprint.route("/clubs/<club_id>", strict_slashes=False)
@oauth.optional()
def read(club_id):
    current_user = User.get(request.user_id) if request.user_id else None

    club = get_requested_record(Club, club_id)

    json = ClubSchema().dump(club).data
    json["isWritable"] = club.is_writable(current_user) or False

    return jsonify(json)


@clubs_blueprint.route("/clubs", methods=["PUT"])
@oauth.required()

def create_club():
    '''register new club'''
    current_user = User.get(request.user_id)
    if not current_user:
        return jsonify(error="invalid-token"), 401

    json = request.get_json()
    if json is None:
        return jsonify(error="invalid-request"), 400

    try:
        data = ClubSchema(only=("name","email","website")).load(json).data
    except ValidationError as e:
        return jsonify(error="validation-failed", fields=e.messages), 422

    if Club.exists(name=data.get("name")):
        return jsonify(error="duplicate-club-name"), 422

    # create the new club
    club = Club(**data)
    club.owner_id = current_user.id

    db.session.add(club)
    db.session.flush()

    # assign the user to the new club
    current_user.club = club

    # create the "user joined club" event
    create_club_join_event(club.id, current_user)

    db.session.commit()

    return jsonify(id=club.id)


@clubs_blueprint.route("/clubs/<club_id>", methods=["POST"], strict_slashes=False)
@oauth.required()
def update(club_id):
    '''For editing club?'''
    current_user = User.get(request.user_id)
    if not current_user:
        return jsonify(error="invalid-token"), 401

    club = get_requested_record(Club, club_id)
    if not club.is_writable(current_user):
        return jsonify(error="forbidden"), 403

    json = request.get_json()
    if json is None:
        return jsonify(error="invalid-request"), 400

    try:
        data = ClubSchema(partial=True).load(json).data
    except ValidationError as e:
        return jsonify(error="validation-failed", fields=e.messages), 422

    if "name" in data:
        name = data.get("name")

        if name != club.name and Club.exists(name=name):
            return jsonify(error="duplicate-club-name"), 422

        club.name = name

    if "website" in data:
        club.website = data.get("website")

    if "email_address" in data:
        club.email_address = data.get("email_address")

    db.session.commit()

    return jsonify()
