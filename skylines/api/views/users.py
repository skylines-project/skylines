from datetime import datetime

from flask import Blueprint
from werkzeug.exceptions import NotFound

from skylines.api.schemas import user_schema
from skylines.model import User
from skylines.api.views.json import jsonify

users = Blueprint('users', 'skylines')


@users.route('/<int:user_id>')
def read(user_id):
    user = User.get(user_id)
    if user is None:
        raise NotFound()

    assert isinstance(user, User)

    created_at = user.created
    assert isinstance(created_at, datetime)

    result = user_schema.dump(user)
    return jsonify(result.data)
