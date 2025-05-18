import sqlalchemy as sa
from flask import abort
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from api import db
from api.models import User


basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user and user.password_hash == password:
        return user


@basic_auth.error_handler
def basic_auth_error(status):
    abort(status)


@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    abort(status)