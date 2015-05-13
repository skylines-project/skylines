from flask import Blueprint, Response, abort, request, current_app
from redis.exceptions import ConnectionError

from skylines.database import db
from skylines.model import Flight, User
from skylines.model.event import create_flight_notifications
from skylines.lib import files
from skylines.lib.upload import UploadStatus, parse_file
from skylines.model.airspace import get_airspace_infringements
from skylines.worker import tasks


upload_blueprint = Blueprint('upload', 'skylines')


@upload_blueprint.route('/upload', methods=('POST', 'GET'))
def upload():
    key = request.headers.get('X-SkyLines-Tracking-Key')
    filename = request.headers.get('X-SkyLines-Filename')

    if not key or not filename:
        return abort(400)

    try:
        key = int(key, 16)
    except:
        abort(400)

    pilot = User.by_tracking_key(key)
    if not pilot:
        current_app.logger.info('Upload for unknown pilot (key: %x)' % (key))
        return Response('Unknown pilot', mimetype='text/plain')

    club_id = pilot.club_id

    filename = files.sanitise_filename(filename)
    filename = files.add_file(filename, request.stream)

    flight, status, fp = parse_file(pilot, pilot.id, club_id, filename)

    if status is UploadStatus.DUPLICATE:
        return Response('Duplicate file', mimetype='text/plain')
    elif status is UploadStatus.MISSING_DATE:
        return Response('Date missing in IGC file', mimetype='text/plain')
    elif status is UploadStatus.PARSER_ERROR:
        return Response('Failed to parse file', mimetype='text/plain')
    elif status is UploadStatus.NO_FLIGHT:
        return Response('No flight found in file', mimetype='text/plain')
    elif status is UploadStatus.FLIGHT_IN_FUTURE:
        return Response('Date of flight in future', mimetype='text/plain')

    db.session.add(flight)
    db.session.flush()

    create_flight_notifications(flight)

    db.session.commit()

    try:
        tasks.analyse_flight.delay(flight.id)
        tasks.find_meetings.delay(flight.id)
    except ConnectionError:
        current_app.logger.info('Cannot connect to Redis server')

    # Check for airspace infringements. If found, don't publish flight
    infringements = get_airspace_infringements(fp, qnh=flight.qnh)
    if infringements:
        return Response('Airspace infringements', mimetype='text/plain')

    # No airspace infringements found, publish immediately.
    flight.privacy_level = Flight.PrivacyLevel.PUBLIC
    db.session.commit()

    return Response('Success', mimetype='text/plain')
