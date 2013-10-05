from __future__ import absolute_import
from celery.utils.log import get_task_logger

from skylines.lib.xcsoar_ import analysis
from skylines import celery, db
from skylines.model import Flight

logger = get_task_logger(__name__)


@celery.task
def analyse_flight(flight_id, full=2048, triangle=6144, sprint=512):
    logger.info("Analysing flight %d" % flight_id)

    if analysis.analyse_flight(Flight.get(flight_id), full, triangle, sprint):
        db.session.commit()
    else:
        logger.warn("Analysis of flight %d failed." % flight_id)
