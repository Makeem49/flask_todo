# custom import
from random import choice

from faker import Faker

from api.app import create_app
from api.models import Users, ToDo
from api.extensions import db
from flask.cli import FlaskGroup
from api.schemas.todos_schema import TodoEntrySchema

app = create_app()
cli = FlaskGroup(app)
todo_entry_schema = TodoEntrySchema()
fake = Faker()


activities = ['read', 'market', 'access social media',
              'visit library', 'grocery store']


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("add_data")
def add_data():
    target_time = 0
    Faker.seed(0)
    for i in range(100):
        target_time = '1:20'
        params = {'first_name': fake.first_name(), 'last_name': fake.last_name(
        ), "email": fake.email(), "password": fake.password()}
        user = Users(**params)
        db.session.add(user)
    db.session.commit()


@app.shell_context_processor
def make_shell_context():
    return dict(Users=Users, db=db, Todo=ToDo)


if __name__ == '__main__':
    cli()
