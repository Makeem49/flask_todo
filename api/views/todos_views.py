# third party import
from flask import Blueprint, request, jsonify, abort
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

todos = Blueprint('todos', __name__, url_prefix='/api/v1.0/todos')

# schemas instance
todo_entry_schema = TodoEntrySchema()
todo_status_schema = TodoStatusSchema()
todo_response_schema = TodoResponseSchema()
todos_response_schema = TodoResponseSchema(many=True)
todo_update_schema = TodoUpdateSchema()
todo_args_schema = TodoArguments()


@todos.route('/', methods=['GET'])
@authenticate(token_auth)
@arguments(todo_args_schema)
@paginated_response('todos')
def get_todos(args):
    """Get todos

    Query todo task for authenticated user. Only return back task created by the authenticated user. 
    """
    current_user = token_auth.current_user()

    search = args.get('search', '')

    task = db.session.query(ToDo).filter_by(user=current_user)

    if search:
        task = task.filter(ToDo.name.ilike(f'%{search}%'))

    return task


@ todos.route('/', methods=['POST'])
@ response(todo_response_schema)
@ body(todo_entry_schema)
@ authenticate(token_auth)
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


@ todos.route('/details/<id>', methods=["GET"])
@ authenticate(token_auth)
@ response(todo_status_schema)
def details(id):
    """Todo details

    This route get the details of the todo associated with an authenticated user.
    """
    current_user = token_auth.current_user()
    todo = ToDo.query.filter_by(id=id).first_or_404()

    if todo.user_id != current_user.id:
        abort(401)
    return todo


@ todos.route('/update/<int:id>', methods=['PUT'])
@ authenticate(token_auth)
@ response(todo_response_schema)
@ other_responses({200: "Task completed, cannot be update"})
@ body(todo_update_schema)
def update(args, id):
    """Update todo

    Authenticated user can update their todo task by the id.
    """
    current_user = token_auth.current_user()
    todo = ToDo.query.filter_by(id=id).first_or_404()

    if todo.user_id != current_user.id:
        abort(401)
        
    if todo and todo.is_completed == False:
        todo.update(args)
    elif todo.is_complete == True:
        return jsonify({"status": "Task completed, cannot be update"}), 200
    return todo, 201


@ todos.route('/start/<id>', methods=['GET'])
@ authenticate(token_auth)
def begin_todo(id):
    """Start task

    Authenticated user can start their todo in thei todo list.
    """
    current_user = token_auth.current_user()
    todo = ToDo.query.filter_by(id=id).first_or_404()

    if current_user.id != todo.user_id:
        abort(401)

    if todo and todo.is_completed == True:
        return jsonify({"status": "Task already completed"}), 200
    elif todo.start_at is not None:
        return jsonify({"status": "You started this task some moment ago."})
    elif todo:
        todo.start()
        return jsonify({'status': 'start'}), 200
    return {}, 200


@ todos.route('/complete_todo/<id>', methods=['PUT'])
@ authenticate(token_auth)
def complete(id):
    """Complete task

    Authicated user mark their todo task co
    """
    current_user = token_auth.current_user()
    todo = ToDo.query.filter_by(id=id).first_or_404()

    if todo.user_id != current_user.id:
        abort(401)

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


@ todos.route('/suspend_todo/<id>', methods=['PUT'])
@ authenticate(token_auth)
def suspend(id):
    """Suspend task"""
    current_user = token_auth.current_user()
    todo = ToDo.query.filter_by(id=id).first_or_404()

    if todo.user_id != current_user.id:
        abort(401)

    todo = ToDo.query.filter_by(id=id).first()
    if todo and todo.is_completed == True:
        return jsonify({"status": "Task already completed, cannot be suspend."}), 200
    elif todo.is_suspended == True:
        return jsonify({"status": "Task already suspended"}), 200
    elif todo and todo.is_completed == False:
        todo.suspend()
        return jsonify({'status': 'suspended'}), 200
    return {}, 404


@ todos.route('/delete_todo/<id>', methods=['DELETE'])
@ authenticate(token_auth)
def delete_todo(id):
    """Delete task"""
    current_user = token_auth.current_user()
    todo = ToDo.query.filter_by(id=id).first_or_404()

    if todo.user_id != current_user.id:
        abort(401)

    todo = ToDo.query.filter_by(id=id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({"status": "deleted"}), 200
    return {}, 404
