from itertools import product
from ..extensions import ma
from ..models import Users
from marshmallow import (ValidationError, post_load, validates,
                         ValidationError, validate, validates_schema)


class EmptySchema(ma.Schema):
    """Empty schema for generic response"""
    pass


class UserLoginSchema(ma.SQLAlchemySchema):
    """Users schema for login"""

    class Meta:
        model = Users

    email = ma.auto_field()
    password = ma.String(required=True, load_only=True,
                         validate=validate.Length(min=3))
    username = ma.auto_field()

    @validates_schema
    def validate_password(self, data, **kwrgs):
        """Check if the password s correct"""
        email = data.get("email")
        password = data.get("password")
        username = data.get('username')
        user = Users.query.filter_by(email=email).first(
        ) or Users.query.filter_by(username=username).first()
        if not user:
            raise ValidationError('Accont not found.')
        if not user.verify_password(password):
            raise ValidationError('Incorrect credentials')

    @post_load
    def make_user(self, data, **kwargs):
        """Make a user instance from value input"""
        identity = data.get('email') or data.get('username')
        user = Users.query.filter_by(email=identity).first(
        ) or Users.query.filter_by(username=identity).first()
        return user


class UserUpdateEmailSchema(ma.SQLAlchemySchema):
    """Users schema for updating user email"""

    class Meta:
        model = Users

    email = ma.auto_field()

    @validates("email")
    def check_email(self, value):
        """Check if the email is already beingg used by a user"""
        user = Users.query.filter_by(email=value).first()
        if user:
            raise ValidationError(
                "Email is already being use, use a different email address.")


class TokenSchema(ma.Schema):
    class Meta:
        ordered = True

    access_token = ma.String()
    refresh_token = ma.String()


class NewPasswordSchema(ma.Schema):
    """Reset password schema"""
    class Meta:
        ordered = True

    password = ma.String(required=True)


class PasswordResetRequestSchema(ma.Schema):
    class Meta:
        ordered = True

    email = ma.String(required=True, validate=[validate.Length(max=120),
                                               validate.Email()])

    @validates("email")
    def check_email(self, value):
        """Check if the email is register a user"""
        user = Users.query.filter_by(email=value).first()
        if not user:
            raise ValidationError(
                "Email not found")
