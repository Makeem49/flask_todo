# standard import
from datetime import time

# third party import
from marshmallow import post_load, validates, ValidationError

# custom import
from api.extensions import ma
from api.models import ToDo


class TodoEntrySchema(ma.SQLAlchemySchema):
    """Todo entry schema"""
    class Meta:
        model = ToDo

    name = ma.auto_field(required=True)
    target_time = ma.auto_field(required=True)

    @post_load
    def create_todo(self, data, **kwargs):
        return ToDo(**data)


class TodoResponseSchema(ma.SQLAlchemySchema):
    """User response schema"""
    class Meta:
        model = ToDo

    user = ma.Hyperlinks(
        {"self": ma.URLFor(
            'todos.details', values=dict(id='<id>'))}
    )


class TodoStatusSchema(ma.SQLAlchemySchema):
    """Todo response schema"""
    class Meta:
        model = ToDo

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(dump_only=True)
    created_at = ma.auto_field(dump_only=True)
    target_time = ma.auto_field(dump_only=True)
    duration = ma.auto_field(dump_only=True)
    start_at = ma.auto_field(dump_only=True)
    completed_at = ma.auto_field(dump_only=True)
    is_suspended = ma.auto_field(dump_only=True)
    is_completed = ma.auto_field(dump_only=True)


class TodoUpdateSchema(ma.SQLAlchemySchema):
    """Todo update schema"""
    class Meta:
        model = ToDo

    name = ma.auto_field(required=True)
    target_time = ma.auto_field(required=True)
