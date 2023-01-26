# standard import
from functools import wraps

# third party import
from flask import request, url_for

# custom import
from api.schemas.users_schema import UserResponseSchema
from api.schemas.todos_schema import TodoResponseSchema
from apifairy import response

user_response = UserResponseSchema()
todo_response = TodoResponseSchema()


def paginated_response(collections, max_limit=25):
    """decorators that return paginated resources. Routes that uses this decorator must return a
    sqlalchemy query for it to work.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # invoke the original function
            query_function = f(*args, **kwargs)
            print(query_function)

            # obtain paginated arguments
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', max_limit, type=int)

            # call paginate method on the returned query
            p = query_function.paginate(page, per_page, max_per_page=max_limit)
            print(p.total, 'total')
            pages = {
                'page': page, 'per_page': per_page, 'total': p.total, 'pages': p.pages
            }

            if p.has_prev:
                pages['prev_url'] = url_for(request.endpoint,
                                            page=p.prev_num, _external=True,
                                            per_page=per_page,
                                            **kwargs)
            else:
                pages['prev_url'] = None

            if p.has_next:
                pages['next_url'] = url_for(request.endpoint,
                                            page=p.next_num, _external=True,
                                            per_page=per_page,
                                            **kwargs)
            else:
                pages['next_url'] = None

            pages['first_url'] = url_for(
                request.endpoint, page=1, per_page=per_page, _external=True)
            pages['last_url'] = url_for(
                request.endpoint, page=p.pages, per_page=per_page, _external=True)

            if collections == 'todos':
                result = [todo_response.dump(todo) for todo in p.items]
            else:
                result = [user_response.dump(user) for user in p.items]

            return {collections: result, "pages": pages}
        return wrapper
    return decorator
