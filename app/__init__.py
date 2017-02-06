from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_oauthlib.provider import OAuth2Provider

from config import config

db = SQLAlchemy()
oauth = OAuth2Provider()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(config_name)

    db.init_app(app)
    oauth.init_app(app)
    from app.api import api
    api.init_app(app)

    return app
