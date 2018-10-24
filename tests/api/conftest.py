import pytest
from werkzeug.datastructures import Headers

from flask import Response, json
from flask.testing import FlaskClient

import config
from skylines import create_api_app


@pytest.fixture(scope="session")
def app():
    """Set up global front-end app for functional tests

    Initialized once per test-run
    """
    app = create_api_app(config.TESTING_CONF_PATH)
    app.test_client_class = ApiClient
    app.response_class = ApiResponse
    return app


class ApiClient(FlaskClient):
    def open(self, *args, **kwargs):
        headers = kwargs.pop("headers", Headers())
        headers.setdefault("User-Agent", "py.test")
        kwargs["headers"] = headers

        json_data = kwargs.pop("json", None)
        if json_data is not None:
            kwargs["data"] = json.dumps(json_data)
            kwargs["content_type"] = "application/json"

        return super(ApiClient, self).open(*args, **kwargs)


class ApiResponse(Response):
    @property
    def json(self):
        return json.loads(self.data)


@pytest.fixture
def client(app):
    with app.test_client(use_cookies=False) as client:
        yield client
