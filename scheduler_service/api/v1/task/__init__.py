from sanic import Blueprint
from sanic_restful import Api

bp = Blueprint("task", "/tasks")
api = Api(bp)

from .main import TaskApi

api.add_resource(TaskApi, "/")
