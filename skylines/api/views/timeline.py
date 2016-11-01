from flask import Blueprint, request
from sqlalchemy.orm import subqueryload, contains_eager
from sqlalchemy.sql.expression import or_

from skylines.api.json import jsonify
from skylines.model.event import Event
from skylines.model import Flight
from .notifications import _filter_query, convert_event

timeline_blueprint = Blueprint('timeline', 'skylines')


@timeline_blueprint.route('/timeline')
def list():
    query = Event.query() \
        .options(subqueryload('actor')) \
        .options(subqueryload('user')) \
        .options(subqueryload('club')) \
        .outerjoin(Event.flight) \
        .options(contains_eager(Event.flight)) \
        .filter(or_(Event.flight == None, Flight.is_rankable())) \
        .order_by(Event.time.desc())

    query = _filter_query(query, request.args)

    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=50)

    events = query.limit(per_page).offset((page - 1) * per_page).all()

    return jsonify(events=(map(convert_event, events)))
