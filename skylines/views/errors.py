from flask import render_template, request

from skylines.views import api


def register(app):
    """ Register error handlers on the given app """

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(500)
    def handle_error(e):
        if request.path.startswith('/api/'):
            return api.jsonify({
                'message': e.description,
            }, status=e.code)

        else:
            return render_template(
                'error.jinja',
                code=e.code,
                name=e.name,
                description=e.description,
            ), e.code
