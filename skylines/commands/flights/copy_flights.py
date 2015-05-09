from flask.ext.script import Command, Option

import os
import shutil
from flask import current_app
from skylines.database import db
from skylines.model import Flight, IGCFile

from selector import selector_options, select


class CopyFlights(Command):
    """ Copy flight files by one or more properties """

    option_list = (
        Option('dest', help='Destination directory'),
    ) + selector_options

    def run(self, dest, **kwargs):
        if not os.path.exists(dest):
            print "Creating destination directory: " + dest
            os.makedirs(dest)

        query = db.session.query(Flight) \
            .join(Flight.takeoff_airport) \
            .join(IGCFile) \
            .order_by(Flight.id)

        query = select(query, **kwargs)

        if not query:
            quit()

        for flight in query:
            print "Flight: " + str(flight.id) + " " + flight.igc_file.filename
            src = os.path.join(
                current_app.config['SKYLINES_FILES_PATH'],
                flight.igc_file.filename
            )
            shutil.copy(src, dest)
