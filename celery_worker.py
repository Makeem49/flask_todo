# from app_folder import make_celery
from api.app import create_app
from api.celery_app import celery
from api.celery_utils import init_celery

app = create_app()

init_celery(celery, app)
