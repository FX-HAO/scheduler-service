from celery import Celery
from sanic import Sanic


def make_celery(app: Sanic) -> Celery:
    celery = Celery(app.import_name)
    celery.conf.update(app.config)
    return celery
