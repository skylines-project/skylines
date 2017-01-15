from flask_script import Manager

from .merge import Merge

manager = Manager(help="Perform operations related to user accounts")
manager.add_command('merge', Merge())
