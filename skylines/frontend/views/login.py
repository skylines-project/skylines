from datetime import datetime

from flask import render_template, redirect, request, url_for, flash, g
from flask.ext.login import login_user, logout_user, current_user
from flask.ext.babel import _

from skylines.model import User
from skylines.frontend.forms import LoginForm


def register(app):
    """ Register the /login and /logout routes on the given app """

    @app.login_manager.user_loader
    def load_user(userid):
        return User.get(userid)

    @app.before_request
    def inject_current_user():
        """
        Inject a current_user variable into the global object. current_user is
        either None or points to the User that is currently logged in.
        """

        if current_user.is_anonymous():
            g.current_user = None
        else:
            g.current_user = current_user

    @app.before_request
    def inject_login_form():
        if g.current_user:
            g.login_form = None
        else:
            g.login_form = LoginForm()

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if g.current_user:
            return redirect(get_next())

        form = g.login_form

        if form.validate_on_submit():
            # Find a user matching the credentials
            user = User.by_credentials(form.email_address.data,
                                       form.password.data)

            # Check if the user wants a cookie
            remember = form.remember_me.data

            # Check if a user was found and try to login
            if user and login_user(user, remember=remember):
                user.login_ip = request.remote_addr
                user.login_time = datetime.utcnow()

                flash(_('You are now logged in. Welcome back, %(user)s!', user=user))
                return redirect(get_next())
            else:
                form.email_address.errors.append(_('Login failed. Please check your email address.'))
                form.password.errors.append(_('Login failed. Please check your password.'))

        return render_template('login.jinja', form=form, next=get_next())

    @app.route('/logout')
    def logout():
        logout_user()
        flash(_('You are now logged out. We hope to see you back soon!'))
        return redirect(get_next())

    def get_next():
        return request.values.get("next") or request.referrer or url_for("index")
