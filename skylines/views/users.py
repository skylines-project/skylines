from flask import Blueprint

from skylines.model import User

users_blueprint = Blueprint('users', 'skylines')


@users_blueprint.route('/')
def index():
    return ', '.join([user.name for user in User.query()])
