
# third party import
from marshmallow import post_load

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

    @post_load
    def create_user(self, data, **kwargs):
        return Users(**data)


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

    