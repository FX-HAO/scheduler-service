from sanic import Blueprint
from sanic_restful import Api

bp = Blueprint("user", "/users")
api = Api(bp)

from .main import UserApi

api.add_resource(UserApi, "/")