from flask import Blueprint, request, render_template, redirect, url_for, abort
from flask.ext.babel import lazy_gettext as l_

from formencode import Schema, All, Invalid
from formencode.validators import FieldsMatch, Email, String, NotEmpty
from sprox.formbase import AddRecordForm, Field
from sprox.validators import UniqueValue
from sprox.sa.provider import SAORMProvider
from tw.forms import PasswordField, TextField

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from skylines.model import DBSession, User, Group
from skylines.forms import BootstrapForm, club

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

    email_address = Field(TextField, All(UniqueValue(SAORMProvider(DBSession),
                                                     __model__, 'email_address'),
                                         Email(not_empty=True)))
    name = Field(TextField, NotEmpty)
    club = club.SelectField
    password = String(min=6)
    verify_password = PasswordField('verify_password',
                                    label_text=l_('Verify Password'))

new_user_form = NewUserForm(DBSession)





@users_blueprint.route('/')
def index():
    users = User.query() \
        .options(joinedload(User.club)) \
        .order_by(func.lower(User.name))

    return render_template('users/list.jinja',
                           active_page='settings',
                           users=users)


def new_post():
    try:
        new_user_form.validate(request.form)
    except Invalid:
        return

    user = User(name=request.form['name'],
                email_address=request.form['email_address'],
                password=request.form['password'])

    if request.form['club']:
        user.club_id = request.form['club']

    user.created_ip = request.remote_addr
    user.generate_tracking_key()
    DBSession.add(user)

    pilots = Group.query(group_name='pilots').first()
    if pilots:
        pilots.users.append(user)

    return user


@users_blueprint.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST' and new_post():
        return redirect(url_for('index'))

    return render_template('users/new.jinja',
                           active_page='users',
                           form=new_user_form)


@users_blueprint.route('/generate_keys')
def generate_keys():
    """Hidden method that generates missing tracking keys."""

    if not request.identity or 'manage' not in request.identity['permissions']:
        abort(401)

    for user in User.query():
        if user.tracking_key is None:
            user.generate_tracking_key()

    DBSession.flush()

    return redirect(url_for('.index'))
