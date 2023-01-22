
# third party import
from marshmallow import post_load, validates, ValidationError

# custom import
from api.extensions import ma
from api.models import Users


class UserEntrySchema(ma.SQLAlchemySchema):
    """User schema"""
    class Meta:
        model = Users

    last_name = ma.auto_field(required=True)
    first_name = ma.auto_field(required=True)
    password = ma.String(required=True)
    email = ma.auto_field(required=True)

    @validates("password")
    def validate_password(self, value):
        pass_len = len(value)
        if pass_len < 6:
            raise ValidationError("Password must be greater than 6.")
        if pass_len > 30:
            raise ValidationError("Password must not be greater than 30.")


class UserResponseSchema(ma.SQLAlchemySchema):
    """User response schema"""
    class Meta:
        model = Users

    user = ma.Hyperlinks(
        {"self": ma.URLFor(
            'users.profile', values=dict(id='<id>'))}
    )


class UserProfileSchema(ma.SQLAlchemySchema):
    """User profile scheme"""
    class Meta:
        model = Users

    id = ma.auto_field(dump_only=True)
    first_name = ma.auto_field(dump_only=True)
    last_name = ma.auto_field(dump_only=True)
    email = ma.auto_field(dump_only=True)
    username = ma.auto_field(dump_only=True)
    confirmed = ma.auto_field(dump_only=True)
    active = ma.auto_field(dump_only=True)
    created_at = ma.auto_field(dump_only=True)
    last_seen = ma.auto_field(dump_only=True)


class UpdateUserSchema(ma.SQLAlchemySchema):
    """Update schema"""
    class Meta:
        model = Users

    first_name = ma.auto_field(required=False)
    last_name = ma.auto_field(required=False)
    email = ma.auto_field(required=False)
    username = ma.auto_field(required=False)

    @validates("username")
    def validate_username(self, value):
        """Validate the username and check if it is not being use."""
        if not value[0].isalpha():
            raise ValidationError("User name must start with a letter.")

        user = Users.query.filter_by(username=value).first()
        if user:
            raise ValidationError('Use a different username.')


class UserArguments(ma.SQLAlchemySchema):
    """Todo arguments schema"""

    class Meta:
        order = True

    page = ma.Integer(required=False)
    per_page = ma.Integer(required=False)


class EmptySchema(ma.Schema):
    pass