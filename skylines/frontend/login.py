import base64

from flask.ext.login import LoginManager

from skylines.model import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@login_manager.header_loader
def load_user_from_header(header_val):
    try:
        header_val = header_val.replace('Basic ', '', 1)
        header_val = base64.b64decode(header_val)
        email, password = header_val.split(':', 1)
        return User.by_credentials(email, password)
    except:
        return None
