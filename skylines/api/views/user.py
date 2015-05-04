from flask import Blueprint, g

from skylines.api import auth
from skylines.api.schemas import current_user_schema
from skylines.api.views.json import jsonify

user = Blueprint('user', 'skylines')


@user.route('/')
@auth.required
def read():
    result = current_user_schema.dump(g.user)
    return jsonify(result.data)
