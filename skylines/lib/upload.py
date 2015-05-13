from flask import current_app
from enum import Enum
from datetime import datetime

from skylines.lib import files
from skylines.lib.md5 import file_md5
from skylines.lib.xcsoar_ import flight_path, analyse_flight
from skylines.model import IGCFile, Flight


class UploadStatus(Enum):
    SUCCESS = 0
    DUPLICATE = 1  # _('Duplicate file')
    MISSING_DATE = 2  # _('Date missing in IGC file')
    PARSER_ERROR = 3  # _('Failed to parse file')
    NO_FLIGHT = 4  # _('No flight found in file')
    FLIGHT_IN_FUTURE = 5  # _('Date of flight in future')


def parse_file(user, pilot_id, club_id, filename):
    # check if the file already exists
    with files.open_file(filename) as f:
        md5 = file_md5(f)
        other = Flight.by_md5(md5)
        if other:
            files.delete_file(filename)
            return (other, UploadStatus.DUPLICATE, None)

    flight = Flight()
    flight.igc_file = IGCFile()
    flight.igc_file.owner = user
    flight.igc_file.filename = filename
    flight.igc_file.md5 = md5
    flight.igc_file.update_igc_headers()

    if flight.igc_file.date_utc is None:
        files.delete_file(filename)
        return (None, UploadStatus.MISSING_DATE, None)

    flight.pilot_id = pilot_id
    flight.club_id = club_id

    flight.model_id = flight.igc_file.guess_model()

    if flight.igc_file.registration:
        flight.registration = flight.igc_file.registration
    else:
        flight.registration = flight.igc_file.guess_registration()

    flight.competition_id = flight.igc_file.competition_id

    fp = flight_path(flight.igc_file, add_elevation=True, max_points=None)

    analyzed = False
    try:
        analyse_flight(flight, fp=fp)
        analyzed = True
    except:
        current_app.logger.exception('analyse_flight() raised an exception')

    if not analyzed:
        files.delete_file(filename)
        return (None, UploadStatus.PARSER_ERROR, None)

    if not flight.takeoff_time or not flight.landing_time:
        files.delete_file(filename)
        return (None, UploadStatus.NO_FLIGHT, None)

    if flight.landing_time > datetime.now():
        files.delete_file(filename)
        return (None, UploadStatus.FLIGHT_IN_FUTURE, None)

    if not flight.update_flight_path():
        files.delete_file(filename)
        return (None, UploadStatus.NO_FLIGHT, None)

    flight.privacy_level = Flight.PrivacyLevel.PRIVATE

    return (flight, UploadStatus.SUCCESS, fp)
