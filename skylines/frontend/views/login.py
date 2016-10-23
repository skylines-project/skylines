import base64

from flask import request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user

from skylines.frontend.ember import send_index
from skylines.model import User
from skylines.schemas import CurrentUserSchema, ValidationError


def register(app):
    """ Register the /login and /logout routes on the given app """

    @app.login_manager.user_loader
    def load_user(userid):
        return User.get(userid)

    @app.login_manager.header_loader
    def load_user_from_header(header_val):
        try:
            header_val = header_val.replace('Basic ', '', 1)
            header_val = base64.b64decode(header_val)
            email, password = header_val.split(':', 1)
            return User.by_credentials(email, password)
        except:
            return None

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

    @app.route('/login')
    def login():
        return send_index()

    @app.route('/session', methods=('PUT',))
    def create_session():
        json = request.get_json()
        if json is None:
            return jsonify(error='invalid-request'), 400

        try:
            data = CurrentUserSchema(only=('email', 'password')).load(json).data
        except ValidationError, e:
            return jsonify(error='validation-failed', fields=e.messages), 422

        user = User.by_credentials(data['email_address'], data['password'])
        if not user or not login_user(user, remember=True):
            logout_user()
            return jsonify(error='wrong-credentials'), 403

        return jsonify()

    @app.route('/session', methods=('DELETE',))
    def delete_session():
        logout_user()
        return jsonify()
