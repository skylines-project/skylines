from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib

from flask import Blueprint, request, render_template, redirect, url_for, abort, current_app, flash, g
from flask.ext.babel import lazy_gettext as l_, _
from werkzeug.exceptions import ServiceUnavailable

from formencode import Schema
from formencode.validators import FieldsMatch, Email
from tw.forms import PasswordField, TextField, HiddenField
from tw.forms.validators import UnicodeString

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from skylines import db
from skylines.model import User, Group
from skylines.model.event import create_new_user_event, create_club_join_event
from skylines.forms import CreatePilotForm, BootstrapForm
from skylines.lib.decorators import validate

users_blueprint = Blueprint('users', 'skylines')


password_match_validator = FieldsMatch(
    'password', 'verify_password',
    messages={'invalidNoMatch': l_('Passwords do not match')})


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
    user = User(name=form.name.data,
                email_address=form.email_address.data,
                password=form.password.data)

    if form.club_id.data:
        user.club_id = form.club_id.data

    user.created_ip = request.remote_addr
    user.generate_tracking_key()
    db.session.add(user)

    pilots = Group.query(group_name='pilots').first()
    if pilots:
        pilots.users.append(user)

    create_new_user_event(user)
    if user.club_id:
        create_club_join_event(user.club_id, user)

    db.session.commit()

    return redirect(url_for('index'))


recover_email_form = BootstrapForm(
    'recover_email_form',
    submit_text=l_("Recover Password"),
    action='recover_email',
    children=[
        TextField('email_address',
                  validator=Email(not_empty=True),
                  label_text=l_('eMail Address'))
    ]
)


recover_password_form = BootstrapForm(
    'recover_password_form',
    submit_text=l_("Recover Password"),
    action='recover_password',
    validator=Schema(chained_validators=(password_match_validator,)),
    children=[
        HiddenField('key'),
        PasswordField('password',
                      validator=UnicodeString(min=6),
                      label_text=l_('Password')),
        PasswordField('verify_password',
                      label_text=l_('Verify Password')),
    ]
)


@users_blueprint.route('/recover')
def recover():
    try:
        key = int(request.values['key'], 16)
    except:
        key = None

    if key:
        user = User.by_recover_key(key)
        if not user:
            abort(404)

        return render_template(
            'generic/form.jinja', active_page='users',
            form=recover_password_form, values=dict(key='%x' % key))

    return render_template(
        'generic/form.jinja', active_page='users',
        form=recover_email_form, values={})


def recover_user_password(user):
    key = user.generate_recover_key(request.remote_addr)

    text = u"""Hi %s,

you have asked to recover your password (from IP %s).  To enter a new
password, click on the following link:

 http://www.skylines-project.org/users/recover?key=%x

The SkyLines Team
""" % (unicode(user), request.remote_addr, key)

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


@users_blueprint.route('/recover_email', methods=['POST'])
@validate(form=recover_email_form, errorhandler=recover)
def recover_email():
    user = User.by_email_address(request.form.get('email_address', None))
    if not user:
        abort(404)

    recover_user_password(user)
    flash('Check your email, we have sent you a link to recover your password.')

    db.session.commit()

    return redirect(url_for('index'))


@users_blueprint.route('/recover_password', methods=['POST'])
@validate(form=recover_password_form, errorhandler=recover)
def recover_password():
    try:
        key = int(request.form['key'], 16)
    except:
        key = None

    user = User.by_recover_key(key)
    if not user:
        abort(404)

    user.password = request.form['password']
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
