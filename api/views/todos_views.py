# third party import
from flask import Blueprint

# custom import

todos = Blueprint('todos', __name__, url_prefix='/api/v1.0')


@todos.route('/add_todo')
def create_todo():
    return {"todo": "created"}
