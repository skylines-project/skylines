from skylines.api.views import api


def register(app):
    """ Register error handlers on the given app """

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(500)
    def handle_http_error(e):
        return api.jsonify({
            'message': e.description,
        }, status=e.code)

    @app.errorhandler(TypeError)
    @app.errorhandler(ValueError)
    def raise_bad_request(e):
        return api.jsonify({
            'message': e.message,
        }, status=400)

    @app.errorhandler(LookupError)
    def raise_not_found(e):
        return api.jsonify({
            'message': e.message,
        }, status=404)
