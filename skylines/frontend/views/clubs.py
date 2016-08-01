from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import func

from skylines.model import Club
from skylines.lib.vary import vary
from skylines.schemas import ClubSchema

clubs_blueprint = Blueprint('clubs', 'skylines')


@clubs_blueprint.route('/')
@vary('accept')
def index():
    if 'application/json' not in request.headers.get('Accept', ''):
        return render_template('ember-page.jinja', active_page='settings')

    clubs = Club.query().order_by(func.lower(Club.name))

    name_filter = request.args.get('name')
    if name_filter:
        clubs = clubs.filter_by(name=name_filter)

    return jsonify(clubs=ClubSchema(only=('id', 'name')).dump(clubs, many=True).data)
