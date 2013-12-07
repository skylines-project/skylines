from skylines.api.views import api


def register(app):
    """ Register error handlers on the given app """

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(500)
    def handle_error(e):
        return api.jsonify({
            'message': e.description,
        }, status=e.code)
