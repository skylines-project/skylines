from flask import redirect

from skylines import app
from skylines.model import User

import skylines.views.about
import skylines.views.i18n
import skylines.views.login


@app.route('/')
def index():
    return redirect('/flights/latest')


@app.route('/users/')
def user_list():
    return ', '.join([user.name for user in User.query()])
