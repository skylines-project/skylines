from flask.ext.script import Command, Option

from skylines.database import db
from skylines.model import Flight, IGCFile
from skylines.lib import files

from selector import selector_options, select


class DeleteFlights(Command):
    """ Delete flights by given criteria """

    option_list = selector_options + (
        Option('--confirm', action='store_true',
               help='confirm to really delete the selected flights'),
    )

    def run(self, confirm, **kwargs):

        query = db.session.query(Flight) \
            .outerjoin(Flight.takeoff_airport) \
            .join(IGCFile) \
            .order_by(Flight.id)

        query = select(query, **kwargs)

        if not query:
            quit()

        for flight in query:
            print "Flight: " + str(flight.id) + " " + flight.igc_file.filename

            if confirm:
                files.delete_file(flight.igc_file.filename)
                db.session.delete(flight)
                db.session.delete(flight.igc_file)
                db.session.commit()
