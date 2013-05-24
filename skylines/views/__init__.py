from datetime import datetime

from flask import render_template, redirect, request, session, url_for, flash
from flask.ext.login import login_user, logout_user, current_user
from flask.ext.babel import _

from skylines import app
from skylines.model import User

@app.route('/')
def index():
    return redirect('/flights/latest')

@app.route('/about')
def about():
    return render_template('about.jinja')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Find a user matching the credentials
        user = User.by_credentials(request.form.get('login', ''),
                                   request.form.get('password', ''))

        # Check if a user was found and try to login
        if user and login_user(user):
            user.login_ip = request.remote_addr
            user.login_time = datetime.utcnow()

            flash(_('You are now logged in. Welcome back, %(user)s!', user=user))
        else:
            flash(_('Sorry, email address or password are wrong. Please try again or register.'), 'warning')

        return redirect(request.args.get("next") or url_for("index"))

    return render_template(
        'login.jinja', next=(request.args.get('next') or request.referrer))

@app.route('/logout')
def logout():
    logout_user()
    flash(_('You are now logged out. We hope to see you back soon!'))
    return redirect(request.args.get("next") or request.referrer or url_for("index"))


@app.route('/set_lang/<language>')
def set_lang(language):
    session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/users/')
def user_list():
    return ', '.join([user.name for user in User.query()])
