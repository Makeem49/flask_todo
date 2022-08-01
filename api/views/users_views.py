# third party import
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

# custom import
from api.models import Users
from api.extensions import db
from api.schemas.users_schemas import (UserEntrySchema,
                                       UserResponseSchema,
                                       UserProfileSchema
                                       )

users = Blueprint('users', __name__, url_prefix='/api/v1.0')

# instance of schemas
user_entry_shema = UserEntrySchema()
user_response_schema = UserResponseSchema()
users_response_schema = UserResponseSchema(many=True)
user_profile_schema = UserProfileSchema()


@users.route('/users', methods=['GET'])
def get_users():
    """Query all user"""
    users = Users.query.all()
    return jsonify({"users": users_response_schema.dump(users)})


@users.route('/register', methods=['POST'])
def create_user():
    """Create a user"""
    params = {**request.json}

    try:
        user = user_entry_shema.load(params)
        user.save()
    except ValidationError as err:
        return jsonify({"error": err.messages}), 406

    return user_response_schema.dump(user), 201


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
    print(user)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"status": "deleted"}), 200
    return jsonify({"status": "No user found"}), 404
