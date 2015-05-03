import pytest


@pytest.fixture(scope="class")
def app_class(request, app):
    request.cls.app = app
