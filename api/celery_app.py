from celery import Celery

 
def make_celery(app_name=__name__):
    redis_uri = 'redis://:devpassword@redis:6379/0'
    return Celery(app_name, backend=redis_uri, broker=redis_uri)


celery = make_celery()
