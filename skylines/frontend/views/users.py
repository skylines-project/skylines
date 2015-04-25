from flask import Blueprint, request, render_template, redirect, url_for, abort, current_app, flash, g
from flask.ext.babel import _
from werkzeug.exceptions import ServiceUnavailable

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from skylines.model import db, User
from skylines.model.event import create_new_user_event
from skylines.frontend.forms import CreatePilotForm, RecoverStep1Form, RecoverStep2Form
from skylines.lib.util import sign_message, unsign_message
from skylines.worker import tasks

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


@users_blueprint.route('/recover', methods=['GET', 'POST'])
def recover():
    key = request.values.get('key')
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
    try:
        tasks.send_mail.delay(
            subject=_('SkyLines password recovery'),
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user.email_address.encode('ascii')],
            text_body=_(
                "Hi %(user)s,"
                "you have asked to recover your password (from IP %(remote_address)s). To enter a new "
                "password, click on the following link: \n\n"
                "%(url)s \n\n"
                "The SkyLines Team",
                user=unicode(user),
                remote_address=request.remote_addr,
                url=url_for(
                    '.recover',
                    key=sign_message(user.recover_key, current_app.config['SECRET_KEY']),
                    _external=True
                )
            ),
            info_log_str='Password recovery'
        )
    except Exception, e:
        current_app.logger.error('Password recovery "send_recover_mail" exception')
        raise ServiceUnavailable(description=_(
            "The mail server is currently not reachable. "
            "Please try again later or contact the developers."))


def recover_step2(key):
    key = unsign_message(key, current_app.config['SECRET_KEY'])
    key = int(key)
    user = User.by_recover_key(key)
    if not user:
        abort(404)

    form = RecoverStep2Form(key=key)
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
