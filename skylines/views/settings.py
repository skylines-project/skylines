from flask import Blueprint, request, render_template, redirect, url_for, abort, g, flash
from flask.ext.babel import _

from skylines import db
from skylines.forms import (
    ChangePasswordForm, EditPilotForm, LiveTrackingSettingsForm
)
from skylines.lib.dbutil import get_requested_record
from skylines.model import User

settings_blueprint = Blueprint('settings', 'skylines')


@settings_blueprint.before_request
def handle_user_param():
    """
    Extracts the `user` parameter from request.values, queries the
    corresponding User model and checks if the model is writeable by the
    current user.
    """

    if not g.current_user:
        abort(403)

    g.user_id = request.values.get('user')

    if g.user_id:
        g.user = get_requested_record(User, g.user_id)
    else:
        g.user = g.current_user

    if not g.user.is_writable(g.current_user):
        abort(403)


@settings_blueprint.route('/')
def index():
    """ Redirects /settings/ to /settings/profile """
    return redirect(url_for('.profile', user=g.user_id))


@settings_blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
    form = EditPilotForm(obj=g.user)
    if not form.validate_on_submit():
        return render_template('settings/profile.jinja', form=form)

    g.user.email_address = form.email_address.data
    g.user.first_name = form.first_name.data
    g.user.last_name = form.last_name.data

    unit_preset = request.form.get('unit_preset', 1, type=int)
    if unit_preset == 0:
        g.user.distance_unit = request.form.get('distance_unit', 1, type=int)
        g.user.speed_unit = request.form.get('speed_unit', 1, type=int)
        g.user.lift_unit = request.form.get('lift_unit', 0, type=int)
        g.user.altitude_unit = request.form.get('altitude_unit', 0, type=int)
    else:
        g.user.unit_preset = unit_preset

    g.user.eye_candy = request.form.get('eye_candy', False, type=bool)

    db.session.commit()

    flash(_('Profile was saved.'), 'success')

    return redirect(url_for('.profile', user=g.user_id))


@settings_blueprint.route('/password', methods=['GET', 'POST'])
def password():
    form = ChangePasswordForm()

    form_validated = form.validate_on_submit()

    if request.method == 'POST' and not (g.user.validate_password(form.password.data) or g.current_user.is_manager()):
        form.current_password.errors.append(_('This password does not match your current password.'))
        form_validated = False

    if not form_validated:
        return render_template('settings/password.jinja', form=form)

    g.user.password = form.password.data
    g.user.recover_key = None

    db.session.commit()

    flash(_('Your password was changed.'), 'success')

    return redirect(url_for('.password', user=g.user_id))


@settings_blueprint.route('/tracking', methods=['GET', 'POST'])
def tracking():
    form = LiveTrackingSettingsForm(obj=g.user)
    if not form.validate_on_submit():
        return render_template('settings/tracking.jinja', form=form)

    g.user.tracking_callsign = form.tracking_callsign.data
    g.user.tracking_delay = request.form.get('tracking_delay', 0)
    db.session.commit()

    flash(_('Live Tracking settings were saved.'), 'success')

    return redirect(url_for('.tracking', user=g.user_id))


@settings_blueprint.route('/tracking/generate-key')
def tracking_generate_key():
    g.user.generate_tracking_key()
    db.session.commit()

    return redirect(url_for('.tracking', user=g.user_id))
