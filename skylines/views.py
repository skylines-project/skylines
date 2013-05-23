from flask import render_template, redirect, request, session, url_for

from skylines import app
from .model import User

@app.route('/')
def index():
    return redirect('/flights/latest')

@app.route('/about')
def about():
    return render_template('about.jinja')

@app.route('/set_lang/<language>')
def set_lang(language):
    session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/users/')
def user_list():
    return ', '.join([user.name for user in User.query()])
