from __future__ import absolute_import
from celery.utils.log import get_task_logger
from sqlalchemy.sql.expression import and_, or_

from skylines.lib.xcsoar_ import analysis
from skylines.worker.celery import celery
from skylines.model import db, Flight, FlightPathChunks, FlightMeetings

from skylines.worker.mail import mail
from flask_mail import Message
from flask import current_app

logger = get_task_logger(__name__)


@celery.task
def analyse_flight(flight_id, full=2048, triangle=6144, sprint=512):
    logger.info("Analysing flight %d" % flight_id)

    if analysis.analyse_flight(Flight.get(flight_id), full, triangle, sprint):
        db.session.commit()
    else:
        logger.warn("Analysis of flight %d failed." % flight_id)


@celery.task
def find_meetings(flight_id):
    logger.info("Searching for near flights of flight %d" % flight_id)

    flight = Flight.get(flight_id)

    # Update FlightPathChunks of current flight
    FlightPathChunks.update_flight_path(flight)

    other_flights = FlightPathChunks.get_near_flights(flight)

    # delete all previous detected points between src and dst
    for key in other_flights:
        FlightMeetings.query() \
            .filter(or_(and_(FlightMeetings.source == flight, FlightMeetings.destination_id == key),
                        and_(FlightMeetings.destination == flight, FlightMeetings.source_id == key))) \
            .delete()

    # Insert new meetings into table
    for flight_id, meetings in other_flights.iteritems():
        other_flight = Flight.get(flight_id)

        for meeting in meetings:
            FlightMeetings.add_meeting(flight, other_flight, meeting['times'][0], meeting['times'][-1])

    db.session.commit()


@celery.task
def send_mail(subject, sender, recipients, text_body=None, html_body=None,
              info_log_str=None):
    msg = Message(
        subject=subject,
        sender=sender,
        recipients=recipients,
        body=text_body,
        html=html_body,
        charset='utf-8',
    )

    if info_log_str is not None:
        logger.warn('Send mail: %s' % info_log_str)

    try:
        with current_app.app_context():
            mail.send(msg)
    except Exception, e:
        logger.warn('Send mail error: %s' % e.message)
