# thrid party import
from flask import Blueprint, jsonify, abort
from email_validator import validate_email, EmailNotValidError
from apifairy import authenticate, body, response, other_responses

# custom import
from api.models import Users, Token
from api.email import send_mail
from api.auth import basic_auth, token_auth
from ..extensions import db
from api.schemas.auth_schema import (UserLoginSchema,
                                     TokenSchema,
                                     EmptySchema,
                                     PasswordResetRequestSchema,
                                     EmptySchema,
                                     UserUpdateEmailSchema,
                                     NewPasswordSchema
                                     )


tokens = Blueprint('tokens', __name__, url_prefix='/api/v1.0/auth')
user_login_schema = UserLoginSchema()
token_schema = TokenSchema()
user_update_email_schema = UserUpdateEmailSchema()
reset_schema = PasswordResetRequestSchema()
password_schema = NewPasswordSchema()


@tokens.route('/login', methods=['POST'])
@authenticate(basic_auth)
@response(token_schema, 201)
@other_responses({401: 'Invalid username/email or password'})
def login():
    """Users login 

    The token are created; access_token and refresh_token. 
    access_token is use to access_restricted pages where user is required to login
    and refresh_token is use to request from new access_token when the access_token 
    expire.
    """
    user = basic_auth.current_user()
    token = user.generate_auth_token()
    db.session.add(token)
    Token.clean()
    db.session.commit()
    return token_schema.dump(token)


@tokens.route('/confirm/<token>', methods=['GET'])
@authenticate(token_auth)
def confirm(token):
    """Confirm user account

    Endpoint verify the user account by confirming the token
    sent to their email when they register their account.
    """
    get_user = token_auth.current_user()
    user = Users.query.filter_by(username=get_user.username).first()
    user = user.confirm_token(token)
    if user:
        return jsonify({"confirmed": user})
    return jsonify({
        "response": "Invalid token or token expired"
    })


@tokens.route('resend_confirmation_token', methods=['POST'])
@authenticate(token_auth)
@response(EmptySchema, 200, description='Resend comfirmatiom tokn to new user who token expire or could not be confirm')
def resend_confirmation_token():
    """Resend confirmation token"""
    user = token_auth.current_user()
    token = user.generate_confirmation_token()
    send_mail.delay(user.email, 'Account Registration',
                    'mail/register', token=token, name=user.username)
    return {}


@tokens.route('/forget_password', methods=['POST'])
@body(reset_schema)
@response(EmptySchema, status_code=204, description='Password reset token')
def forget_password(args):
    """Forget password

    Endpoint where user can request for a password reset link by 
    entering the user email address use to register the account.
    """
    email = args.get('email')
    try:
        valid_email = validate_email(email)
    except EmailNotValidError:
        return jsonify({"error": "Not a valid email address."})
    user = Users.query.filter_by(email=email).first()
    print(user)
    if user:
        token = user.generate_new_email_confirmation_token(email)
        send_mail.delay(email, "Account Recovery",
                        'mail/reset_password', token=token)
    return {}


@tokens.route('/reset_password/<token>', methods=['POST'])
@body(password_schema)
@response(EmptySchema)
def reset_password(args, token):
    """Reset password"""
    password = args.get('password')
    user = Users.new_password(token, password)
    if user:
        return {}
    return abort(408)


@tokens.route('/refresh', methods=['PUT'])
@body(token_schema)
@response(token_schema, 201, description='Newly issued access and refresh tokens')
@other_responses({401: 'Invalid access or refresh token'})
def refresh_token(args):
    """Refresh access token

    The client can the refresh token in the body of the request or in a `refresh_token` cookie.
    The access token must be present in the body of the request.
    """
    access_token = args.get('access_token')
    refresh_token = args.get('refresh_token')

    if not access_token or not refresh_token:
        abort(401)
    token = Users.verify_refresh_token(refresh_token, access_token)
    if not token:
        abort(401)
    token.expire()
    new_token = token.user.generate_auth_token()
    db.session.add_all([token, new_token])
    db.session.commit()
    return token_schema.dump(new_token)


@tokens.route('/change_email', methods=['POST'])
@authenticate(basic_auth)
@body(user_update_email_schema)
@response(EmptySchema, status_code=200, description='Users email update')
def change_email(args):
    """Change email address"""
    email = args.get('email')
    user = basic_auth.current_user()
    token = user.generate_new_email_confirmation_token(email)
    send_mail(email, "Change Account Email",
              'mail/change_email', name=user.last_name, token=token)
    return {}


@tokens.route('/confirm_new_email_token/<token>', methods=['GET'])
@authenticate(token_auth)
def confirm_email_address(token):
    """Confirm user new email

    Verify user new email address which the user intend to change to. If the email correct and active,  confirmed response will be returned. If the email or the link is tempered with, or expired, a 406 response with error will be returned. 
    """
    get_user = token_auth.current_user()
    user = get_user.confirm_new_email_token(token)
    if user:
        return jsonify({'status': 'confirmed'})
    return jsonify({'status': 'error'}), 406


@tokens.route("/logout", methods=["DELETE"])
@authenticate(token_auth)
@response(EmptySchema, status_code=204, description='Users log out')
def logout():
    """Log out user"""
    user = token_auth.current_user()
    user.revoke_all()
    return {}
