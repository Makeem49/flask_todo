# third party import
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from apifairy import body, response, other_responses, authenticate, arguments

# custom import
from api.models import ToDo
from api.schemas.todos_schema import (TodoEntrySchema,
                                      TodoStatusSchema,
                                      TodoResponseSchema,
                                      TodoUpdateSchema,
                                      TodoArguments
                                      )
from api.extensions import db
from api.decorators import paginated_response
from api.auth import token_auth

todos = Blueprint('todos', __name__, url_prefix='/api/v1.0/todo')

# schemas instance
todo_entry_schema = TodoEntrySchema()
todo_status_schema = TodoStatusSchema()
todo_response_schema = TodoResponseSchema()
todos_response_schema = TodoResponseSchema(many=True)
todo_update_schema = TodoUpdateSchema()
todo_args_schema = TodoArguments()


@todos.route('/todos/', methods=['GET'])
@arguments(todo_args_schema)
@paginated_response('todos')
def get_todos(args):
    """Get todos"""
    todos = ToDo.query
    return todos


@todos.route('/create', methods=['POST'])
@response(todo_response_schema)
@body(todo_entry_schema)
@authenticate(token_auth)
def create(args):
    """
    Create todo

    This endpoint allow user to create todo. The target time represent the time the user 
    wanted to use to accomplish the task. 
    """
    user = token_auth.current_user()
    todo = ToDo(**args)
    todo.user_id = user.id
    db.session.add(todo)
    db.session.commit()
    return todo


@todos.route('/todo_details/<id>', methods=["GET"])
def details(id):
    todo = ToDo.query.filter_by(id=id).first()
    if todo:
        return todo_status_schema.dump(todo), 200
    return {}, 204


@todos.route('/update_todo/<id>', methods=['PUT'])
def update(id):
    params = {**request.json}
    todo = ToDo.query.filter_by(id=id).first()
    try:
        if todo and todo.is_completed == False:
            todo_update = todo_update_schema.load(params)
            todo.update(todo_update)
            return todo_response_schema.dump(todo), 201
        elif todo.is_complete == True:
            return jsonify({"status": "Task completed, cannot be update"}), 200
    except ValidationError as err:
        return jsonify({"error": err.messages}), 406
    return {}, 404


@todos.route('/start/<id>', methods=['PUT'])
def begin_todo(id):
    todo = ToDo.query.filter_by(id=id).first()
    if todo and todo.is_completed == True:
        return jsonify({"status": "Task already completed"}), 200
    elif todo.start_at is not None:
        return jsonify({"status": "You started this task some moment ago."})
    elif todo:
        todo.start()
        return jsonify({'status': 'start'}), 200
    return {}, 404


@todos.route('/complete_todo/<id>', methods=['PUT'])
def complete(id):
    todo = ToDo.query.filter_by(id=id).first()
    if todo and todo.is_suspended == True:
        return jsonify({"status": "Task has suspended by you."})
    elif todo.start_at is None:
        return jsonify({"status": "You need to start this task first."})
    elif todo and todo.is_completed == False:
        todo.complete()
        todo.done()
        todo.time_diff()
        return jsonify({'status': 'completed'}), 200
    elif todo.is_completed == True:
        return jsonify({"status": "Task already completed."})
    return {}, 404


@todos.route('/suspend_todo/<id>', methods=['PUT'])
def suspend(id):
    todo = ToDo.query.filter_by(id=id).first()
    if todo and todo.is_completed == True:
        return jsonify({"status": "Task already completed, cannot be suspend."}), 200
    elif todo.is_suspended == True:
        return jsonify({"status": "Task already suspended"}), 200
    elif todo and todo.is_completed == False:
        todo.suspend()
        return jsonify({'status': 'suspended'}), 200
    return {}, 404


@todos.route('/delete_todo/<id>', methods=['DELETE'])
def delete_todo(id):
    todo = ToDo.query.filter_by(id=id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({"status": "deleted"}), 200
    return {}, 404
