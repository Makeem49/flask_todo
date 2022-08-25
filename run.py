# custom import
from api.app import create_app
from api.models import Users, ToDo
from api.extensions import db
from flask.cli import FlaskGroup
from api.schemas.todos_schema import TodoEntrySchema

app = create_app()
cli = FlaskGroup(app)
todo_entry_schema = TodoEntrySchema()


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("add_data")
def add_data():
    target_time = 0
    for i in range(100):
        target_time = '1:20'
        params = {'name': 'read', 'target_time': target_time}
        todo = todo_entry_schema.load(params)
        db.session.add(todo)
    db.session.commit()


@app.shell_context_processor
def make_shell_context():
    return dict(Users=Users, db=db)


if __name__ == '__main__':
    cli()
