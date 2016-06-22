from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import func

from skylines.model import Club
from skylines.lib.vary import vary_accept

clubs_blueprint = Blueprint('clubs', 'skylines')


@clubs_blueprint.route('/')
@vary_accept
def index():
    clubs = Club.query().order_by(func.lower(Club.name))

    if 'application/json' in request.headers.get('Accept', ''):
        json = []
        for c in clubs:
            json.append({
                'id': c.id,
                'name': unicode(c),
            })

        return jsonify(clubs=json)

    return render_template('ember-page.jinja', active_page='settings')
