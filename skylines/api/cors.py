from flask import request


class CORS(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.after_request(self.add_cors_headers)

    @staticmethod
    def add_cors_headers(response):
        if 'Origin' in request.headers:
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin'))
            response.headers.add('Access-Control-Allow-Credentials', 'true')

            if 'Access-Control-Request-Methods' in request.headers:
                response.headers.add('Access-Control-Allow-Methods',
                                     request.headers.get('Access-Control-Request-Methods'))

            if 'Access-Control-Request-Headers' in request.headers:
                response.headers.add('Access-Control-Allow-Headers',
                                     request.headers.get('Access-Control-Request-Headers'))

        return response


cors = CORS()
