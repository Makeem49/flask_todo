# third party import
from flask import Blueprint, jsonify, request, abort
from marshmallow import ValidationError
from apifairy import authenticate, response, body, arguments

# custom import
from api.models import Users
from api.extensions import db
from api.schemas.users_schema import (UserEntrySchema,
                                      UserResponseSchema,
                                      UserProfileSchema,
                                      UserArguments,
                                      UpdateUserSchema,
                                      EmptyResponseSchema
                                      )
from ..decorators import paginated_response
from api.auth import token_auth, basic_auth
from api.decorators.permissions import is_user

users = Blueprint('users', __name__, url_prefix='/api/v1.0/users')

# instance of schemas
user_entry_shema = UserEntrySchema()
user_response_schema = UserResponseSchema()
users_response_schema = UserResponseSchema(many=True)
my_profile_schema = UserProfileSchema()
user_profile_schema = UserProfileSchema(exclude=['email', "id"])
user_args_schema = UserArguments()
user_update_schema = UpdateUserSchema()


@users.route('/', methods=['GET'])
@authenticate(token_auth)
@paginated_response('users')
@arguments(user_args_schema)
def get_users(args):
    """Query all user

    Retrieve all users in the database
    """
    return Users.query


@users.route('/', methods=['POST'])
@response(user_response_schema, 201)
@body(user_entry_shema)
def create_user(args):
    """Create a user

    Add a new user to the database
    """
    print(args)
    user = Users(**args)
    db.session.add(user)
    db.session.commit()
    return user


@users.route('/me', methods=['GET'])
@authenticate(token_auth)
@response(my_profile_schema)
@is_user
def me(id):
    """My Profile

    Get profile of any user using the user id
    """
    user = Users.query.filter_by(id=id).first()
    return user


@users.route('/<id>', methods=['GET'])
@authenticate(token_auth)
@response(user_profile_schema)
def profile(id):
    """User Profile

    Get profile of any user using the user id
    """
    user = Users.query.filter_by(id=id).first_or_404()
    return user


@users.route('/<int:id>', methods=['PUT'])
@authenticate(token_auth)
@response(user_profile_schema)
@body(user_update_schema)
def update(args, id):
    """Update user 

    Only user who own the account can only update ther account. 
    """
    user = Users.query.filter_by(id=id).first_or_404()
    current_user = token_auth.current_user()
    if current_user.id != user.id:
        abort(401)

    user.update(args)
    print(user)
    return user


@users.route('/<id>', methods=['DELETE'])
@authenticate(token_auth)
@response(EmptyResponseSchema)
@is_user
def delete_account(id):
    """Delete user

    User can delete their own account.     
    """
    user = Users.query.filter_by(id=id).first_or_404()
    current_user = token_auth.current_user()
    if current_user.id != user.id:
        abort(401)

    db.session.delete(user)
    db.session.commit()
    return user, 204
