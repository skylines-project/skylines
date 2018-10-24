from flask import Blueprint, request
from babel import negotiate_locale as _negotiate_locale

from skylines.api.json import jsonify

i18n_blueprint = Blueprint("i18n", "skylines")


@i18n_blueprint.route("/locale")
def negotiate_locale():
    available = request.args.get("available", "").split(",")
    available = [locale for locale in available if locale != ""]

    if len(available) == 0:
        return jsonify(error="invalid-request"), 400

    preferred = [headers[0] for headers in request.accept_languages]

    locale = _negotiate_locale(preferred, available, sep="-")

    return jsonify(locale=locale)
