# standard import
import os

# third party import
from flask import Flask, url_for, redirect

# custom import
from api.errors import errors
from api.views.users_views import users
from api.views.todos_views import todos
from api.extensions import apifairy, db, ma, migrate
from api.views.tokens import tokens


def create_app(settings_override=None):
    """Create flask application instance"""
    app = Flask(__name__, instance_relative_config=True)

    if settings_override is None:
        """Use the application default configuration is settings_override is None"""
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(settings_override)

    try:
        os.makedirs(app.instance_path)
    except:
        OSError

    @app.route('/doc')
    def index():  # pragma: no cover
        return redirect(url_for('apifairy.docs'))

    @app.route('/')
    def root():
        return redirect(url_for('todos.get_todos'))

    # register bleuprint
    app.register_blueprint(errors)
    app.register_blueprint(users)
    app.register_blueprint(todos)
    app.register_blueprint(tokens)

    # initializing extensions
    extensions(app)

    return app


def extensions(app):
    """Initializing flask extensions"""
    apifairy.init_app(app)
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
