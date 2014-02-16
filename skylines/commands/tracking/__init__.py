from flask.ext.script import Manager

from .clear import Clear
from .export import Export
from .fill_missing_keys import FillMissingKeys
from .generate import Generate
from .generate_through_daemon import GenerateThroughDaemon
from .server import Server
from .stats import Stats

manager = Manager(help="Perform operations related to live tracking")
manager.add_command('clear', Clear())
manager.add_command('export', Export())
manager.add_command('fill-missing-keys', FillMissingKeys())
manager.add_command('generate', Generate())
manager.add_command('generate-through-daemon', GenerateThroughDaemon())
manager.add_command('runserver', Server())
manager.add_command('stats', Stats())
