from flask import Blueprint, render_template
from sqlalchemy import func
from skylines.model import Club

clubs_blueprint = Blueprint('clubs', 'skylines')


@clubs_blueprint.route('/')
def index():
    clubs = Club.query().order_by(func.lower(Club.name))
    return render_template(
        'clubs/list.jinja', active_page='settings', clubs=clubs)
