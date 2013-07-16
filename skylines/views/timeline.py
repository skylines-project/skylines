from flask import Blueprint, render_template, request
from sqlalchemy.orm import joinedload

from skylines.lib.util import str_to_bool
from skylines.model.notification import Event, group_events
from .notifications import _filter_query

timeline_blueprint = Blueprint('timeline', 'skylines')


@timeline_blueprint.route('/')
def index():
    query = Event.query() \
        .options(joinedload('actor')) \
        .options(joinedload('flight')) \
        .order_by(Event.time.desc())

    query = _filter_query(query, request.args)

    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=50)

    query = query.limit(per_page)
    query = query.offset((page - 1) * per_page)

    events = query.all()
    events_count = len(events)

    if request.args.get('grouped', True, type=str_to_bool):
        events = group_events(events)

    template_vars = dict(events=events, types=Event.Type)

    if page > 1:
        template_vars['prev_page'] = page - 1
    if events_count == per_page:
        template_vars['next_page'] = page + 1

    return render_template('timeline/list.jinja', **template_vars)
