from flask.ext.script import Option
from sqlalchemy import func
from datetime import datetime

from skylines.model import Airport, Flight


selector_options = (
    Option('--date-from', help='Date from (YYYY-MM-DD)'),
    Option('--date-to', help='Date to (YYYY-MM-DD)'),
    Option('--uploaded-from', help='Date from (YYYY-MM-DD)'),
    Option('--uploaded-to', help='Date to (YYYY-MM-DD)'),
    Option('--private', action='store_true',
           help='Process private flights, too'),
    Option('--country-code', help='Country code of the start airport'),
    Option('--airport-name', help='Airport name of the start airport'),
    Option('ids', metavar='ID', nargs='*', type=int,
           help='Any number of flight IDs.'),
)


def select(q, **kwargs):
    if kwargs.get('ids'):
        print "ids == " + str(kwargs.get('ids'))
        q = q.filter(Flight.id.in_(kwargs.get('ids')))

    if kwargs.get('date_from'):
        try:
            date_from = datetime.strptime(kwargs.get('date_from'), "%Y-%m-%d")
            q = q.filter(Flight.takeoff_time >= date_from)
            print "takeoff_time >= " + str(date_from)
        except:
            print "Cannot parse date-from"
            return None

    if kwargs.get('date_to'):
        try:
            date_to = datetime.strptime(kwargs.get('date_to'), "%Y-%m-%d")
            q = q.filter(Flight.takeoff_time < date_to)
            print "takeoff_time < " + str(date_to)
        except:
            print "Cannot parse date-to"
            return None

    if kwargs.get('uploaded_from'):
        try:
            uploaded_from = datetime.strptime(kwargs.get('uploaded_from'), "%Y-%m-%d")
            q = q.filter(Flight.time_created >= uploaded_from)
            print "time_created >= " + str(uploaded_from)
        except:
            print "Cannot parse uploaded-from"
            return None

    if kwargs.get('uploaded_to'):
        try:
            uploaded_to = datetime.strptime(kwargs.get('uploaded_to'), "%Y-%m-%d")
            q = q.filter(Flight.time_created < uploaded_to)
            print "time_created < " + str(uploaded_to)
        except:
            print "Cannot parse uploaded-to"
            return None

    if not kwargs.get('private'):
        print "privacy_level == PUBLIC"
        q = q.filter(Flight.privacy_level == Flight.PrivacyLevel.PUBLIC)

    if kwargs.get('country_code'):
        country_code = kwargs.get('country_code')

        q = q.join(Flight.takeoff_airport)
        q = q.filter(func.lower(Airport.country_code) == func.lower(country_code))
        print "takeoff_airport country code: " + country_code

    if kwargs.get('airport_name'):
        airport_name = kwargs.get('airport_name')

        q = q.join(Flight.takeoff_airport)
        q = q.filter(func.lower(Airport.name) == func.lower(airport_name))
        print "takeoff_airport name: " + airport_name

    return q
