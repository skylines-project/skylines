import time
from functools import wraps

from itsdangerous import JSONWebSignatureSerializer
from flask import Blueprint, request, abort, jsonify, current_app

from flask.ext.oauthlib.provider import OAuth2Provider
from flask_oauthlib.provider import OAuth2RequestValidator
from flask_oauthlib.provider.oauth2 import log
from flask_oauthlib.utils import decode_base64
from oauthlib.common import to_unicode
from oauthlib.oauth2.rfc6749.tokens import random_token_generator

from skylines.database import db
from skylines.model import User, Client, RefreshToken, AccessToken


class CustomProvider(OAuth2Provider):
    def __init__(self, *args, **kwargs):
        super(CustomProvider, self).__init__(*args, **kwargs)
        self.blueprint = Blueprint('oauth', __name__)

    def init_app(self, app):
        super(CustomProvider, self).init_app(app)
        app.config.setdefault('OAUTH2_PROVIDER_TOKEN_GENERATOR', self.generate_token)
        app.config.setdefault('OAUTH2_PROVIDER_REFRESH_TOKEN_GENERATOR', random_token_generator)

        app.jws = JSONWebSignatureSerializer(app.config.get('SECRET_KEY'))

        app.register_blueprint(self.blueprint)

    def generate_token(self, request):
        token = {
            'user': request.user.id,
            'exp': int(time.time() + request.expires_in),
        }

        if request.scopes is not None:
            token['scope'] = ' '.join(request.scopes)

        return current_app.jws.dumps(token)

    def verify_request(self, scopes):
        if request.authorization:
            from skylines.model import User

            user = User.by_credentials(
                request.authorization.username,
                request.authorization.password,
            )

            request.user_id = user.id if user else None
            return (user is not None), None

        else:
            valid, req = super(CustomProvider, self).verify_request(scopes)

            request.user_id = req.access_token.user_id if valid else None

            return valid, req

    def required(self, *args, **kwargs):
        return self.require_oauth(*args, **kwargs)

    def optional(self, *scopes):
        """Enhance resource with specified scopes."""
        def wrapper(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                for func in self._before_request_funcs:
                    func()

                if hasattr(request, 'oauth') and request.oauth:
                    return f(*args, **kwargs)

                valid, req = self.verify_request(scopes)

                for func in self._after_request_funcs:
                    valid, req = func(valid, req)

                if not valid and (not req or 'Authorization' in req.headers or req.access_token):
                    if self._invalid_response:
                        return self._invalid_response(req)
                    return abort(401)
                request.oauth = req
                return f(*args, **kwargs)
            return decorated
        return wrapper


class CustomRequestValidator(OAuth2RequestValidator):
    def __init__(self):
        super(CustomRequestValidator, self).__init__(
            clientgetter=lambda client_id: Client(),
            tokengetter=self.tokengetter,
            grantgetter=None,
            usergetter=User.by_credentials,
            tokensetter=self.tokensetter,
        )

    @staticmethod
    def tokengetter(access_token=None, refresh_token=None):
        """ Retrieve a token record using submitted access token or refresh token. """
        if access_token:
            return AccessToken.from_jwt(access_token)

        elif refresh_token:
            return RefreshToken.query(refresh_token=refresh_token).first()

    @staticmethod
    def tokensetter(token, request, *args, **kwargs):
        """ Save a new token to the database.

        :param token: Token dictionary containing access and refresh tokens, plus token type.
        :param request: Request dictionary containing information about the client and user.
        """

        if request.grant_type != 'refresh_token':
            tok = RefreshToken(
                refresh_token=token['refresh_token'],
                user_id=request.user.id,
            )
            db.session.add(tok)
            db.session.commit()

    def rotate_refresh_token(self, request):
        return False

    def authenticate_client(self, request, *args, **kwargs):

        auth = request.headers.get('Authorization', None)
        if auth:
            try:
                _, s = auth.split(' ')
                client_id, client_secret = decode_base64(s).split(':')
                client_id = to_unicode(client_id, 'utf-8')
            except Exception as e:
                log.debug('Authenticate client failed with exception: %r', e)
                return False
        else:
            client_id = request.client_id

        client = self._clientgetter(client_id)
        if not client:
            log.debug('Authenticate client failed, client not found.')
            return False

        return self.authenticate_client_id(client_id, request)


oauth = CustomProvider()
oauth._validator = CustomRequestValidator()


@oauth.blueprint.route('/oauth/token', methods=['POST'])
@oauth.token_handler
def access_token(*args, **kwargs):
    return None


@oauth.blueprint.route('/oauth/revoke', methods=['POST'])
@oauth.revoke_handler
def revoke_token():
    pass


@oauth.invalid_response
def invalid_require_oauth(req):
    message = req.error_message if req else 'Unauthorized'
    return jsonify(error='invalid_token', message=message), 401
