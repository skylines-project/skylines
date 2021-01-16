import pytest
import requests
from mock import patch, Mock
from shutil import copyfile

from skylines.lib import files
from skylines.model import IGCFile
from skylines import weglide

from tests.data import users, igcs


@pytest.fixture
def test_data(db_session):
    # create test user
    john = users.john()
    db_session.add(john)

    # create IGC file
    igc_file = igcs.simple(john)
    igc_file.weglide_status = 1
    db_session.add(igc_file)

    path = files.filename_to_path(igc_file.filename)
    copyfile(igcs.simple_path, path)

    db_session.flush()

    return (john, igc_file)


def test_happy_path(db_session, test_data):
    (_, igc_file) = test_data

    response = [
        {
            "id": 42,
            "user": {"id": 123, "name": "John Doe"},
            "igc_file": {
                "id": 999,
                "file": "123/igcfiles/foo.igc",
            },
        }
    ]

    with patch("requests.post") as mock:
        mock.return_value.status_code = 201
        mock.return_value.json = Mock()
        mock.return_value.json.return_value = response

        weglide.upload(igc_file.id, "123", "2020-01-07")

    mock.assert_called_once()
    assert mock.call_args.args == ("https://api.weglide.org/v1/igcfile",)
    assert mock.call_args.kwargs.get("data") == {
        "user_id": "123",
        "date_of_birth": "2020-01-07",
    }
    assert mock.call_args.kwargs.get("files")

    igc_file = db_session.query(IGCFile).get(igc_file.id)
    assert igc_file.weglide_status == 201
    assert igc_file.weglide_data == response


def test_failure_with_missing_database_record():
    with patch("requests.post") as mock:
        weglide.upload(42, "239", "1987-02-24")

    mock.assert_not_called()


def test_with_422_json_error(db_session, test_data):
    (_, igc_file) = test_data

    with patch("requests.post") as mock:
        mock.return_value.status_code = 500
        mock.return_value.json = Mock()
        mock.return_value.json.return_value = {"details": "foo"}

        weglide.upload(igc_file.id, "123", "2020-01-07")

    igc_file = db_session.query(IGCFile).get(igc_file.id)
    assert igc_file.weglide_status == 500
    assert igc_file.weglide_data == {"details": "foo"}


def test_with_500_non_json_error(db_session, test_data):
    (_, igc_file) = test_data

    with patch("requests.post") as mock:
        mock.return_value.status_code = 500
        mock.return_value.json = Mock()
        mock.return_value.json.side_effect = ValueError("Boom!")

        weglide.upload(igc_file.id, "123", "2020-01-07")

    igc_file = db_session.query(IGCFile).get(igc_file.id)
    assert igc_file.weglide_status == 500
    assert igc_file.weglide_data is None


def test_with_network_error(db_session, test_data):
    (_, igc_file) = test_data

    with patch("requests.post") as mock:
        mock.side_effect = requests.exceptions.ConnectionError()

        weglide.upload(igc_file.id, "123", "2020-01-07")

    igc_file = db_session.query(IGCFile).get(igc_file.id)
    assert igc_file.weglide_status == 2
    assert igc_file.weglide_data is None


def test_with_generic_error(db_session, test_data):
    (_, igc_file) = test_data

    with patch("requests.post") as mock:
        mock.side_effect = Exception("Boom!")

        weglide.upload(igc_file.id, "123", "2020-01-07")

    igc_file = db_session.query(IGCFile).get(igc_file.id)
    assert igc_file.weglide_status == 2
    assert igc_file.weglide_data is None
