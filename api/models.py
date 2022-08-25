# standard import
from email.policy import default
import uuid
from datetime import datetime, timedelta
import secrets

# third import
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Text
from werkzeug.security import generate_password_hash, check_password_hash

# custom import
from api.extensions import db


class CommonAttribute:
    def save(self):
        """Save user to db"""
        db.session.add(self)
        db.session.commit()

    def update(self, params):
        """Update user"""
        for attr, value in params.items():
            setattr(self, attr, value)

        db.session.commit()


class Token(db.Model, CommonAttribute):
    """Token model"""
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(256), nullable=False)
    refresh_token = db.Column(db.String(256), nullable=False)
    access_exp = db.Column(db.String(256), nullable=False)
    refresh_exp = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # relationship
    user = db.relationship('Users', back_populates='tokens')

    def generate(self):
        self.access_token = secrets.token_urlsafe()
        self.refresh_token = secrets.token_urlsafe()
        self.access_exp = datetime.utcnow() + timedelta(minutes=15)
        self.refresh_exp = datetime.utcnow() + timedelta(days=15)

    def expire(self):
        self.access_exp = datetime.utcnow()
        self.refresh_exp = datetime.utcnow()

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day"""
        yesterday = datetime.utcnow() - timedelta(days=1)
        tokens = db.session.query(Token).filter(
            Token.refresh_exp < yesterday).all()
        for token in tokens:
            db.session.delete(token)
        db.session.commit()

    def __repr__(self) -> str:
        return "Token created"


class Users(db.Model, CommonAttribute):
    """User model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=True, unique=True)
    password_hash = db.Column(Text, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow)

    # relationship
    todos = db.relationship('ToDo', back_populates='user',
                            lazy='dynamic', cascade='all, delete-orphan')
    tokens = db.relationship(Token, back_populates='user',
                             lazy='select', cascade='all, delete-orphan')

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

        db.session.commit()

    def is_active(self):
        return self.active

    def generate_auth_token(self):
        """Generate authentication token for user"""
        token = Token(user=self)
        token.generate()

    @staticmethod
    def verify_access_token(access_token):
        """Method to verify token"""

        token = Token.query.filter_by(access_token=access_token).first()
        if token:
            if token.access_exp > datetime.utcnow():
                token.user.ping()
                db.session.commit()
                return token.user
        else:
            return None

    @staticmethod
    def verify_refresh_token(refresh_token, access_token):
        """Method to verify refresh token"""

        token = db.session.query(Token).filter_by(
            refresh_token=refresh_token, access_token=access_token).first()

        if token:
            if token.refresh_exp > datetime.utcnow():
                return token

            # if any one tried to refresh a token with an expired on,
            # the token for the that particular user should be revoke as
            # a security measure.
            token.user.revoke_all()
            db.session.commit()

    def revoke_all(self):
        """Revoke all token"""
        tokens = db.session.query(Token).filter(Token.user == self).all()
        for token in tokens:
            db.session.delete(token)
        db.session.commit()

    def __repr__(self) -> str:
        return f"User {self.first_name}"


class ToDo(db.Model, CommonAttribute):
    """ToDo model"""
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    target_time = db.Column(db.Time, nullable=True)
    duration = db.Column(db.Time, nullable=True)
    start_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    is_suspended = db.Column(db.Boolean, nullable=False, default=False)
    is_completed = db.Column(db.Boolean, nullable=True, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # relationship
    user = db.relationship("Users", back_populates="todos")

    def start(self):
        """Method to start the task"""
        if self.is_suspended == True:
            self.is_suspended = False

        self.start_at = datetime.utcnow()

        db.session.commit()

    def complete(self):
        """Method to create the time the task was completed."""
        self.completed_at = datetime.utcnow()

        db.session.commit()

    def suspend(self):
        """Method to suspend a task"""
        self.is_suspended = True

        db.session.commit()

    def done(self):
        """Method to set is_completed to True"""
        self.is_completed = True

        db.session.commit()

    def time_diff(self):
        """Time difference between start and completed time"""
        diff = self.completed_at - self.start_at
        self.duration = self.completed_at + diff

        db.session.commit()

    def __repr__(self) -> str:
        return f"{self.name.capitalize()} task created"
