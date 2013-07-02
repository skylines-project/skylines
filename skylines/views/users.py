from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib

from flask import Blueprint, request, render_template, redirect, url_for, abort, current_app, flash, g
from flask.ext.babel import lazy_gettext as l_, _
from werkzeug.exceptions import ServiceUnavailable

from formencode import Schema, All
from formencode.validators import FieldsMatch, Email, String, NotEmpty
from sprox.formbase import AddRecordForm, Field
from sprox.validators import UniqueValue
from sprox.sa.provider import SAORMProvider
from tw.forms import PasswordField, TextField, HiddenField
from tw.forms.validators import UnicodeString

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from skylines import db
from skylines.model import User, Group
from skylines.forms import BootstrapForm, club
from skylines.lib.decorators import validate

users_blueprint = Blueprint('users', 'skylines')


password_match_validator = FieldsMatch(
    'password', 'verify_password',
    messages={'invalidNoMatch': l_('Passwords do not match')})

user_validator = Schema(chained_validators=(password_match_validator,))


class NewUserForm(AddRecordForm):
    __base_widget_type__ = BootstrapForm
    __model__ = User
    __required_fields__ = ['password']
    __limit_fields__ = ['email_address', 'name', 'password', 'verify_password', 'club']
    __base_validator__ = user_validator
    __field_widget_args__ = {
        'email_address': dict(label_text=l_('eMail Address')),
        'name': dict(label_text=l_('Name')),
        'club': dict(label_text=l_('Club')),
        'password': dict(label_text=l_('Password')),
    }

    email_address = Field(TextField, All(UniqueValue(SAORMProvider(db.session),
                                                     __model__, 'email_address'),
                                         Email(not_empty=True)))
    name = Field(TextField, NotEmpty)
    club = club.SelectField
    password = String(min=6)
    verify_password = PasswordField('verify_password',
                                    label_text=l_('Verify Password'))

new_user_form = NewUserForm(db.session)


@users_blueprint.route('/')
def index():
    users = User.query() \
        .options(joinedload(User.club)) \
        .order_by(func.lower(User.name))

    return render_template('users/list.jinja',
                           active_page='settings',
                           users=users)


@users_blueprint.route('/new')
def new():
    return render_template('users/new.jinja',
                           active_page='users',
                           form=new_user_form)


@users_blueprint.route('/new', methods=['POST'])
@validate(new_user_form, new)
def new_post():
    user = User(name=request.form['name'],
                email_address=request.form['email_address'],
                password=request.form['password'])

    if request.form['club']:
        user.club_id = request.form['club']

    user.created_ip = request.remote_addr
    user.generate_tracking_key()
    db.session.add(user)

    pilots = Group.query(group_name='pilots').first()
    if pilots:
        pilots.users.append(user)

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
