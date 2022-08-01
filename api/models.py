# standard import
from email.policy import default
import uuid
from datetime import datetime

# third import
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Text
from werkzeug.security import generate_password_hash, check_password_hash

# custom import
from api.extensions import db


class Users(db.Model):
    """User model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=True)
    password_hash = db.Column(Text, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow,)

    @property
    def password():
        raise AttributeError('Password is not callable.')

    @password.setter
    def password(self, password):
        """Hash user password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Confirm user password with stored hash"""
        return check_password_hash(self.password_hash, password)

    def ping(self):
        """Update user last seen"""
        self.last_seen = datetime.utcnow()

    def is_active(self):
        return self.active

    def save(self):
        """Save user to db"""
        db.session.add(self)
        db.session.commit()
        

    def update(self, params):
        """Update user"""
        for attr, value in params.items():
            setattr(self, attr, value)

        db.session.commit()

    def __repr__(self) -> str:
        return f"User {self.first_name}"


class ToDo(db.Model):
    """ToDo model"""
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=False)
    suspended = db.Column(db.Boolean, nullable=False, default=False)
    duration = db.Column(db.Time, nullable=False)
    completed = db.Column(db.Boolean, nullable=True)

    def __repr__(self) -> str:
        return f"{self.name.capitalize()} task created"
