from flask import Blueprint
from webargs.flaskparser import use_args
from werkzeug.exceptions import NotFound

from skylines.api.schemas import user_schema, user_list_schema
from skylines.api.args import pagination_args
from skylines.model import User
from skylines.api.json import jsonify

users = Blueprint('users', 'skylines')


@users.route('/users', strict_slashes=False)
@use_args(pagination_args)
def list(args):
    offset = (args['page'] - 1) * args['per_page']
    limit = args['per_page']

    users = User.query().offset(offset).limit(limit)
    result = user_list_schema.dump(users, many=True)

    return jsonify(result.data)


@users.route('/users/<int:user_id>')
def read(user_id):
    user = User.get(user_id)
    if user is None:
        raise NotFound()

    result = user_schema.dump(user)
    return jsonify(result.data)
