from datetime import date

from flask import Blueprint, request, g
from sqlalchemy import func
from sqlalchemy.sql.expression import desc, over
from sqlalchemy.orm import eagerload

from skylines.api.json import jsonify
from skylines.database import db
from skylines.model import User, Club, Flight, Airport
from skylines.lib.table_tools import Pager, Sorter
from skylines.schemas import AirportSchema, ClubSchema, UserSchema

ranking_blueprint = Blueprint("ranking", "skylines")

from query_db import _handle_request_rank

@ranking_blueprint.route("/ranking/pilots")
def pilots():
    data = _handle_request_rank(User, "pilot_id")

    user_schema = UserSchema(only=("id", "name", "club"))

    json = []
    for pilot, count, total, rank in data["result"]:
        row = {
            "rank": rank,
            "flights": count,
            "points": total,
            "user": user_schema.dump(pilot).data,
        }

        json.append(row)

    return jsonify(ranking=json, total=g.paginators["result"].count)


@ranking_blueprint.route("/ranking/clubs")
def clubs():
    data = _handle_request_rank(Club, "club_id")

    club_schema = ClubSchema(only=("id", "name"))

    json = []
    for club, count, total, rank in data["result"]:
        row = {
            "rank": rank,
            "flights": count,
            "points": total,
            "club": club_schema.dump(club).data,
        }

        json.append(row)

    return jsonify(ranking=json, total=g.paginators["result"].count)


@ranking_blueprint.route("/ranking/airports")
def airports():
    data = _handle_request_rank(Airport, "takeoff_airport_id")

    airport_schema = AirportSchema(only=("id", "name", "countryCode"))

    json = []
    for airport, count, total, rank in data["result"]:
        row = {
            "rank": rank,
            "flights": count,
            "points": total,
            "airport": airport_schema.dump(airport).data,
        }

        json.append(row)

    return jsonify(ranking=json, total=g.paginators["result"].count)
