from flask.ext.script import Manager
from skylines.model import db, AircraftModel

manager = Manager(help="Perform operations related to the aircraft tables")


@manager.command
def add_model(name, kind=0, index=0):
    """ Add a new aircraft model to the database """

    model = AircraftModel(name=name, kind=kind)
    if index > 0:
        model.igc_index = model.dmst_index = index

    db.session.add(model)
    db.session.commit()
