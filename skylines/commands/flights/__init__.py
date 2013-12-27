from flask.ext.script import Manager

from .analysis import Analyze, AnalyzeDelayed
from .copy_flights import CopyFlights
from .delete_flights import DeleteFlights
from .update_flight_paths import UpdateFlightPaths

manager = Manager(help="Perform operations related to recorded flights")
manager.add_command('analyze', Analyze())
manager.add_command('analyze-delayed', AnalyzeDelayed())
manager.add_command('copy-flights', CopyFlights())
manager.add_command('delete-flights', DeleteFlights())
manager.add_command('update-flight-paths', UpdateFlightPaths())
