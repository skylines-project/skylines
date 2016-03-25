from flask import Blueprint, request

from skylines.model import User
from skylines.api.oauth import oauth
from skylines.api.schemas import current_user_schema
from skylines.api.views.json import jsonify

user = Blueprint('user', 'skylines')


@user.route('/user/')
@user.route('/user')
@oauth.required()
def read():
    user = User.get(request.user_id)
    result = current_user_schema.dump(user)
    return jsonify(result.data)
