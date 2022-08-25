# third party import
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from apifairy import authenticate, response, body, arguments

# custom import
from api.models import Users
from api.extensions import db
from api.schemas.users_schemas import (UserEntrySchema,
                                       UserResponseSchema,
                                       UserProfileSchema,
                                       UserArguments
                                       )
from ..decorators import paginated_response
from api.auth import token_auth

users = Blueprint('users', __name__, url_prefix='/api/v1.0')

# instance of schemas
user_entry_shema = UserEntrySchema()
user_response_schema = UserResponseSchema()
users_response_schema = UserResponseSchema(many=True)
user_profile_schema = UserProfileSchema()
user_args_schema = UserArguments()


@users.route('/users/', methods=['GET'])
@paginated_response('users')
@arguments(user_args_schema)
# @authenticate(token_auth)
def get_users(args):
    """Query all user

    Retrieve all users in the database
    """
    return Users.query


@users.route('/register', methods=['POST'])
@response(user_response_schema, 201)
@body(user_entry_shema)
def create_user(args):
    """Create a user
    
    Add a new user to the database
    """
    user = Users(**args)
    db.session.add(user)
    db.session.commit()
    return user


@users.route('/profile/<id>', methods=['GET'])
def profile(id):
    """Get a user with iD"""
    user = Users.query.filter_by(id=id).first()
    if user is None:
        user = Users.query.filter_by(username=id).first()
    if user:
        return user_profile_schema.dump(user), 200
    return {}


@users.route('/update_details/<int:id>', methods=['PUT'])
# # @authenticate(token_auth)
# @body(user_profile_schema)
# @response(user_profile_schema, 200)
def update(id):
    """Update user details"""
    params = {**request.json}
    user = Users.query.filter_by(id=id).first()
    if user:
        user.update(params)
        return user_profile_schema.dump(user), 200
    return jsonify({"status": "Not found"}), 404


@users.route('/delete_my_account/<id>', methods=['DELETE'])
def delete_account(id):
    user = Users.query.filter_by(id=id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"status": "deleted"}), 200
    return jsonify({"status": "No user found"}), 404
