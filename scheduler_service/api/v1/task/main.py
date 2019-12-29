from sanic.request import Request
from sanic_restful import Resource, reqparse

from scheduler_service.api.decorators import login_require
from scheduler_service.models import User


class TaskApi(Resource):
    decorators = [login_require]

    async def get(self, request: Request, user: User):
        doc = await request.app.mongo_db.task.find_one({"uid": user.id})
        return doc or {}