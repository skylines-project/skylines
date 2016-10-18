from flask import request, jsonify
from babel import negotiate_locale


def register(app):

    @app.route('/locale')
    def resolve_locale():
        available = request.args.get('available', '').split(',')
        available = filter(lambda it: it != '', available)

        if len(available) == 0:
            return jsonify(error='invalid-request'), 400

        preferred = map(lambda it: it[0], request.accept_languages)

        locale = negotiate_locale(preferred, available, sep='-')

        return jsonify(locale=locale)
