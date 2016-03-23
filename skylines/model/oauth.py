from datetime import datetime
from flask import current_app
from itsdangerous import BadSignature

from skylines.database import db


class Client(object):
    client_id = 'default'
    client_secret = None
    client_type = 'public'
    redirect_uris = []
    default_redirect_uri = ''
    default_scopes = []
    allowed_grant_types = ['password', 'refresh_token']


class AccessToken(object):
    client_id = Client.client_id
    token_type = 'Bearer'
    user = None

    @classmethod
    def from_jwt(cls, access_token):
        try:
            decoded = current_app.jws.loads(access_token)
        except BadSignature:
            return None

        return AccessToken(
            access_token,
            user_id=decoded['user'],
            expires=datetime.utcfromtimestamp(decoded['exp'])
        )

    def __init__(self, access_token, user_id, expires, scopes=None):
        self.access_token = access_token
        self.user_id = user_id
        self.expires = expires
        self.scopes = scopes or []

    def delete(self):
        pass


class RefreshToken(db.Model):
    __tablename__ = 'token'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    client_id = Client.client_id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', foreign_keys=[user_id])
    refresh_token = db.Column(db.String(255), unique=True)
    scopes = []

    def delete(self):
        db.session.delete(self)
        db.session.commit()
