from flask.ext.script import Command, Option

import os
import shutil
from datetime import datetime
from time import mktime, strptime
from flask import current_app
from sqlalchemy import func
from skylines.model import db, Airport, Flight, IGCFile


class CopyFlights(Command):
    """ Copy flight files by one or more properties """

    option_list = (
        Option('--flight_id', type=int, help='ID of the flight'),
        Option('--country_code', help='Country code of the start airport'),
        Option('--airport_name', help='Airport name of the start airport'),
        Option('--date_from', help='Date from (YYYY-MM-DD)'),
        Option('--date_to', help='Date to (YYYY-MM-DD)'),
        Option('dest', help='Destination directory'),
    )

    def run(self, flight_id, country_code, airport_name,
            date_from, date_to, dest):

        if not os.path.exists(dest):
            print "Creating destination directory: " + dest
            os.makedirs(dest)

        query = db.session.query(Flight) \
            .join(Flight.takeoff_airport) \
            .join(IGCFile) \
            .order_by(Flight.id)

        if flight_id is not None:
            print "Filter by flight id: " + str(flight_id)
            query = query.filter(Flight.id == flight_id)

        if country_code is not None:
            print "Filter by takeoff airport country code: " + str(country_code)
            query = query.filter(
                func.lower(Airport.country_code) ==
                func.lower(str(country_code)))

        if airport_name is not None:
            print "Filter by takeoff airport name: " + str(airport_name)
            query = query.filter(
                func.lower(Airport.name) ==
                func.lower(str(airport_name)))

        if date_from is not None:
            try:
                date_from = strptime(date_from, "%Y-%m-%d")
            except:
                print "Cannot parse from date."
                quit()

            query = query.filter(
                Flight.takeoff_time >=
                datetime.fromtimestamp(mktime(date_from)))

        if date_to is not None:
            try:
                date_to = strptime(date_to, "%Y-%m-%d")
            except:
                print "Cannot parse to date."
                quit()

            query = query.filter(
                Flight.takeoff_time <=
                datetime.fromtimestamp(mktime(date_to)))

        for flight in query:
            print "Flight: " + str(flight.id) + " " + flight.igc_file.filename
            src = os.path.join(
                current_app.config['SKYLINES_FILES_PATH'],
                flight.igc_file.filename
            )
            shutil.copy(src, dest)
