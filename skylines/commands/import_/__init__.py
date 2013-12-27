from flask.ext.script import Manager

from .airspace import AirspaceCommand
from .dmst_index import DMStIndex
from .mwp import MWP
from .srtm import SRTM
from .welt2000 import Welt2000

manager = Manager(help="Import external data into the database")
manager.add_command('airspace', AirspaceCommand())
manager.add_command('dmst-index', DMStIndex())
manager.add_command('mwp', MWP())
manager.add_command('srtm', SRTM())
manager.add_command('welt2000', Welt2000())
