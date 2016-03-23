from flask import Blueprint, g

from skylines.api.oauth import oauth
from skylines.api.schemas import current_user_schema
from skylines.api.views.json import jsonify

user = Blueprint('user', 'skylines')


@user.route('/user/')
@user.route('/user')
@oauth.required()
def read():
    result = current_user_schema.dump(g.user)
    return jsonify(result.data)
