import pytest


@pytest.fixture(scope="function", autouse=True)
def autouse_db_session(db_session):
    pass
