from flask_script import Manager

from .merge import Merge
from .email import Email

manager = Manager(help="Perform operations related to user accounts")
manager.add_command("email", Email())
manager.add_command("merge", Merge())
