from celery import Celery
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_oauthlib.provider import OAuth2Provider
from flask_mail import Mail
from flask_httpauth import HTTPBasicAuth

from config import config

db = SQLAlchemy()
oauth = OAuth2Provider()
mail = Mail()
auth = HTTPBasicAuth()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(config_name)

    db.init_app(app)
    oauth.init_app(app)
    mail.init_app(app)
    from app.api import api
    api.init_app(app)

    return app

def make_celery(app):
    celery = Celery(app.import_name)
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery