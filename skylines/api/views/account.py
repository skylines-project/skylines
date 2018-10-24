from flask import Blueprint, request

from skylines.api.json import jsonify
from skylines.database import db
from skylines.api.oauth import oauth
from skylines.model import User

account_blueprint = Blueprint("account", "skylines")


@account_blueprint.route("/account", methods=["DELETE"], strict_slashes=False)
@oauth.required()
def delete_account():
    current_user = User.get(request.user_id)

    json = request.get_json()
    if json is None:
        return jsonify(error="invalid-request"), 400

    if "password" not in json:
        return jsonify(error="password-missing"), 400

    if not current_user.validate_password(json["password"]):
        return jsonify(error="wrong-password"), 403

    current_user.delete()
    db.session.commit()

    return jsonify()
