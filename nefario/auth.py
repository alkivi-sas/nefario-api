"""Module that manage authentification."""
from flask import jsonify, g, current_app
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from pepper import Pepper, PepperException

from . import db
from .models import User

# Init Auth
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')


@basic_auth.verify_password
def verify_password(nickname, password):
    """
    Password verification callback.

    ---
    securityDefinitions:
      UserSecurity:
        type: basic
    """
    if not nickname or not password:
        return False

    api = Pepper('http://master:8080')
    try:
        auth = api.login(nickname, password, 'pam')
    except PepperException:
        return False

    user = User.query.filter_by(nickname=nickname).first()
    if not user:
        user = User.create({'nickname': nickname})

    current_app.logger.debug('auth')
    current_app.logger.debug(auth)
    user.token = auth['token']
    db.session.add(user)
    db.session.commit()

    g.current_user = user

    return True


@token_auth.verify_token
def verify_token(token):
    """
    Token verification callback.

    ---
    securityDefinitions:
      UserSecurity:
        type: apiKey
        in: header
        name: token
    """
    user = User.query.filter_by(token=token).first()
    if user is None:
        return False
    db.session.add(user)
    db.session.commit()
    g.current_user = user
    return True


@basic_auth.error_handler
@token_auth.error_handler
def auth_error():
    """Return a 401 error to the client."""
    return (jsonify({'error': 'authentication required'}), 401,
            {'WWW-Authenticate': 'Bearer realm="Authentication Required"'})
