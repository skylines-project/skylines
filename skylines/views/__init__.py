from flask import render_template, redirect

from skylines import app
from skylines.model import User

import skylines.views.i18n
import skylines.views.login


@app.route('/')
def index():
    return redirect('/flights/latest')


@app.route('/about')
def about():
    return render_template('about.jinja')


@app.route('/users/')
def user_list():
    return ', '.join([user.name for user in User.query()])
