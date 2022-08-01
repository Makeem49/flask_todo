# custom import 
from api.app import create_app
from api.models import Users
from api.extensions import db 
from flask.cli import FlaskGroup

app = create_app()
cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@app.shell_context_processor
def make_shell_context():
    return dict(Users=Users, db=db)

if __name__ == '__main__':
    cli()