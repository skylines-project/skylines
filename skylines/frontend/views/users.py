from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib

from flask import Blueprint, request, render_template, redirect, url_for, abort, current_app, flash, g
from flask.ext.babel import _
from werkzeug.exceptions import ServiceUnavailable

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from skylines.database import db
from skylines.model import User
from skylines.model.event import create_new_user_event
from skylines.frontend.forms import CreatePilotForm, RecoverStep1Form, RecoverStep2Form

users_blueprint = Blueprint('users', 'skylines')


@users_blueprint.route('/')
def index():
    users = User.query() \
        .options(joinedload(User.club)) \
        .order_by(func.lower(User.name))

    return render_template('users/list.jinja',
                           active_page='settings',
                           users=users)


@users_blueprint.route('/new', methods=['GET', 'POST'])
def new():
    form = CreatePilotForm()
    if form.validate_on_submit():
        return new_post(form)

    return render_template('users/new.jinja', form=form)


def new_post(form):
    user = User(
        first_name=form.first_name.data,
        last_name=form.last_name.data,
        email_address=form.email_address.data,
        password=form.password.data
    )

    user.created_ip = request.remote_addr
    db.session.add(user)

    create_new_user_event(user)

    db.session.commit()

    flash(_('Welcome to SkyLines, %(user)s! You can now log in and share your flights with the world!', user=user))

    return redirect(url_for('index'))


def hex(value):
    return int(value, 16)


@users_blueprint.route('/recover', methods=['GET', 'POST'])
def recover():
    key = request.values.get('key', type=hex)
    if key is None:
        return recover_step1()
    else:
        return recover_step2(key)


def recover_step1():
    form = RecoverStep1Form()
    if form.validate_on_submit():
        return recover_step1_post(form)

    return render_template('users/recover_step1.jinja', form=form)


def recover_step1_post(form):
    user = User.by_email_address(form.email_address.data)
    if not user:
        abort(404)

    user.generate_recover_key(request.remote_addr)
    send_recover_mail(user)
    flash('Check your email, we have sent you a link to recover your password.')

    db.session.commit()
    return redirect(url_for('index'))


def send_recover_mail(user):
    text = u"""Hi %s,

you have asked to recover your password (from IP %s).  To enter a new
password, click on the following link:

 http://skylines.aero/users/recover?key=%x

The SkyLines Team
""" % (unicode(user), request.remote_addr, user.recover_key)

    msg = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
    msg['Subject'] = 'SkyLines password recovery'
    msg['From'] = current_app.config['EMAIL_FROM']
    msg['To'] = user.email_address.encode('ascii')
    msg['Date'] = formatdate(localtime=1)

    try:
        smtp = smtplib.SMTP(current_app.config['SMTP_SERVER'])
        smtp.ehlo()
        smtp.sendmail(current_app.config['EMAIL_FROM'].encode('ascii'),
                      user.email_address.encode('ascii'), msg.as_string())
        smtp.quit()

    except:
        raise ServiceUnavailable(description=_(
            "The mail server is currently not reachable. "
            "Please try again later or contact the developers."))


def recover_step2(key):
    user = User.by_recover_key(key)
    if not user:
        abort(404)

    form = RecoverStep2Form(key='%x' % key)
    if form.validate_on_submit():
        return recover_step2_post(key, form)

    return render_template('users/recover_step2.jinja', form=form)


def recover_step2_post(key, form):
    user = User.by_recover_key(key)
    if not user:
        abort(404)

    user.password = form.password.data
    user.recover_key = None

    flash(_('Password changed.'))

    db.session.commit()

    return redirect(url_for('index'))


@users_blueprint.route('/generate_keys')
def generate_keys():
    """Hidden method that generates missing tracking keys."""

    if not g.current_user or not g.current_user.is_manager():
        abort(403)

    for user in User.query():
        if user.tracking_key is None:
            user.generate_tracking_key()

    db.session.commit()

    return redirect(url_for('.index'))
