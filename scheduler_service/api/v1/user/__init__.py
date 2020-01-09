from sanic import Blueprint
from sanic_restful import Api

bp = Blueprint("user", "/users")
api = Api(bp)

from .main import UserApi
from .token import AuthTokenApi

api.add_resource(UserApi, "")
api.add_resource(AuthTokenApi, "/auth/token")
