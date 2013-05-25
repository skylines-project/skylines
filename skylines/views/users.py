from flask import Blueprint, render_template

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from skylines.model import User

users_blueprint = Blueprint('users', 'skylines')


@users_blueprint.route('/')
def index():
    users = User.query() \
        .options(joinedload(User.club)) \
        .order_by(func.lower(User.name))

    return render_template('users/list.jinja',
                           active_page='settings',
                           users=users)
