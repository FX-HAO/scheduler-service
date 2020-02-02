from sanic import Blueprint
from sanic_restful import Api

bp = Blueprint("task", "/tasks")
api = Api(bp)

from .main import TasksApi

api.add_resource(TasksApi, "")
