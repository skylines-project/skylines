from flask.ext.script import Manager
from skylines.database import db
from skylines.model import AircraftModel

manager = Manager(help="Perform operations related to the aircraft tables")


@manager.command
def add_model(name, kind=0, index=0):
    """ Add a new aircraft model to the database """

    model = AircraftModel(name=name, kind=kind)
    if index > 0:
        model.igc_index = model.dmst_index = index

    db.session.add(model)
    db.session.commit()


@manager.command
def remove_model(index):
    """ Remove the aircraft model from database """
    AircraftModel.query(id=index).delete()
    db.session.commit()


@manager.command
def list():
    """ Shows the list of aircrafts"""
    aircraftModels = AircraftModel.query().all()
    return aircraftModels


@manager.command
def kind_enum():
    """ Shows possible values of kind property"""
    print """
0 unspecified
1 glider
2 motor glider
3 paraglider
4 hangglider
5 ul glider
"""
