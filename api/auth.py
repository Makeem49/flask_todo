# third party import
from werkzeug.exceptions import Unauthorized, Forbidden
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask import current_app

# custom import
from api.models import Users
from api.extensions import db


basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(email, password):
    if email and password:
        user = Users.query.filter_by(email=email).first(
        ) or Users.query.filter_by(username=email).first()
        if user and user.verify_password(password):
            return user


@basic_auth.error_handler
def basic_auth_error(status=401):
    error = (Forbidden if status == 403 else Unauthorized)()
    return {
        'code': error.code,
        'message': error.name,
        'description': error.description
    }, error.code, {'WWW-Authenticate': 'Form'}


@token_auth.verify_token
def verify_token(access_token):
    if current_app.config['DISABLE_AUTH']:
        user = db.session.get(Users, 1)
        user.ping()
        return user

    if access_token:
        return Users.verify_access_token(access_token)


@token_auth.error_handler
def token_auth_error(status=401):
    error = (Forbidden if status == 403 else Unauthorized)()
    return {
        'code': error.code,
        'message': error.name,
        'description': error.description,
    }, error.code
