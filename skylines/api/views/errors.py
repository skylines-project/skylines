from werkzeug.exceptions import HTTPException, InternalServerError
from skylines.api.json import jsonify


def register(app):
    """
    Register error handlers on the given app

    :type app: flask.Flask
    """

    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(405)
    @app.errorhandler(500)
    def handle_http_error(e):
        if not isinstance(e, HTTPException):
            e = InternalServerError()

        data = getattr(e, 'data', None)
        if data:
            message = data['message']
        else:
            message = e.description

        return jsonify(message=message), e.code

    @app.errorhandler(422)
    def handle_bad_request(err):
        # webargs attaches additional metadata to the `data` attribute
        data = getattr(err, 'data')
        if data:
            # Get validations from the ValidationError object
            messages = data['exc'].messages
        else:
            messages = ['Invalid request']

        return jsonify(messages=messages), 422

    @app.errorhandler(TypeError)
    @app.errorhandler(ValueError)
    def raise_bad_request(e):
        return jsonify(message=e.message), 400

    @app.errorhandler(LookupError)
    def raise_not_found(e):
        return jsonify(message=e.message), 404
