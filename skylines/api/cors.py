import os

from flask import current_app, request


_DEFAULT_ORIGINS = (
    "https://skylines.aero",
    "https://www.skylines.aero",
)

_DEV_ORIGINS = (
    "http://localhost",
    "http://localhost:5000",
    "http://localhost:4200",
    "http://127.0.0.1",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:4200",
)


def _get_allowed_origins():
    """Return the set of allowed CORS origins.

    In order of precedence:
    1. CORS_ORIGINS env var (comma-separated)
    2. Production defaults + dev origins when DEBUG is True
    3. Production defaults only
    """
    env_origins = os.getenv("CORS_ORIGINS")
    if env_origins:
        return set(o.strip() for o in env_origins.split(",") if o.strip())

    allowed = set(_DEFAULT_ORIGINS)
    if current_app.config.get("DEBUG"):
        allowed.update(_DEV_ORIGINS)
    return allowed


class CORS(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.after_request(self.add_cors_headers)

    @staticmethod
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin and origin in _get_allowed_origins():
            response.headers.add("Access-Control-Allow-Origin", origin)
            response.headers.add("Access-Control-Allow-Credentials", "true")

            if "Access-Control-Request-Methods" in request.headers:
                response.headers.add(
                    "Access-Control-Allow-Methods",
                    request.headers.get("Access-Control-Request-Methods"),
                )

            if "Access-Control-Request-Headers" in request.headers:
                response.headers.add(
                    "Access-Control-Allow-Headers",
                    request.headers.get("Access-Control-Request-Headers"),
                )

        return response


cors = CORS()
