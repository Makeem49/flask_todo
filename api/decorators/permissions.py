from functools import wraps
from apifairy import authenticate
from flask import abort

from api.auth import token_auth
from api.models import Users


def is_user(f):
    @wraps(f)
    @authenticate(token_auth)
    def wrapper(*args, **kwargs):
        current_user = token_auth.current_user()

        user = f(current_user.id, *args, **kwargs)

        if user.id != current_user.id:
            abort(401)

        return user

    return wrapper

