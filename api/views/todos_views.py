# third party import
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from api.models import ToDo

# custom import
from api.schemas.todos_schema import (TodoEntrySchema,
                                      TodoStatusSchema,
                                      TodoResponseSchema,
                                      TodoUpdateSchema
                                      )
from api.extensions import db

todos = Blueprint('todos', __name__, url_prefix='/api/v1.0')

# schemas instance
todo_entry_schema = TodoEntrySchema()
todo_status_schema = TodoStatusSchema()
todo_response_schema = TodoResponseSchema()
todos_response_schema = TodoResponseSchema(many=True)
todo_update_schema = TodoUpdateSchema()


@todos.route('/todos', methods=['GET'])
def get_todos():
    todos = ToDo.query.all()
    return jsonify({'todo': todos_response_schema.dump(todos)}), 200


@todos.route('/add_todo', methods=['POST'])
def create_todo():
    params = {**request.json}
    print(params)
    try:
        todo = todo_entry_schema.load(params)
        todo.save()
    except ValidationError as err:
        return jsonify({"error": err.messages}), 406

    return todo_response_schema.dump(todo), 201


@todos.route('/todo_details/<id>', methods=["GET"])
def details(id):
    todo = ToDo.query.filter_by(id=id).first()
    if todo:
        return todo_status_schema.dump(todo), 200
    return {}, 404


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
        return jsonify({"status" : "Task already suspended"}), 200
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
