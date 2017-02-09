# coding: utf-8
from flask import g
from flask_httpauth import HTTPBasicAuth
from app.models import User
from .. import api, auth


@auth.verify_password
def verify_password(email, password):
    user = User._filter(email=email)
    if not user:
        return user
    g.current_user = user
    return user.verify_password(password)
