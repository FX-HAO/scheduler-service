from bson import ObjectId
from sanic.request import Request
from sanic.exceptions import InvalidUsage
from sanic_restful import Resource, reqparse

from scheduler_service import mongo_db
from scheduler_service.api.decorators import login_require
from scheduler_service.models import User


tasks_post_parse = reqparse.RequestParser()
tasks_post_parse.add_argument("name", required=True)
tasks_post_parse.add_argument("interval", type=int)

task_parse = reqparse.RequestParser()
task_parse.add_argument("request_url", required=True)
task_parse.add_argument("callback_url")


class TasksApi(Resource):
    decorators = [login_require]

    async def get(self, request: Request, user: User):
        doc = await mongo_db.task.find_one({"uid": user.id})
        return doc or {}

    async def post(self, request: Request, user: User):
        docs = await mongo_db.task.find({"uid": user.id}).to_list()
        if len(docs) >= request.app.config['MAX_TASKS']:
            raise InvalidUsage("NUMBER OF TASKS EXCEEDS THE LIMIT")

        params = tasks_post_parse.parse_args(request)
        await mongo_db.tasks.insert({
            "name": params.name,
            "interval_time": params.interval,
            "user_id": user.id
        })
        return


class TaskApi(Resource):
    decorators = [login_require]

    async def get(self, request: Request, user: User, task_id: int):
        doc = await mongo_db.task.find_one({"_id": ObjectId(task_id)})
        return doc or {}

    async def post(self, request: Request, user: User, task_id: int):
        doc = await mongo_db.task.find_one({"_id": ObjectId(task_id)})
        if len(doc['urls']) >= request.app.config['MAX_URLS']:
            raise InvalidUsage("NUMBER OF URLS EXCEEDS THE LIMIT")
        params = task_parse.parse_args(request)
        url = {
            "request_url": params.request_url,
            "callback_url": params.callback_url
        }
        await mongo_db.task.update({"_id": ObjectId(task_id)},
                                   {"$push": {
                                       "urls": url
                                   }})

    async def delete(self, request: Request, user: User, task_id: int):
        await mongo_db.task.delete({"_id": ObjectId(task_id)})

    async def patch(self, request: Request, user: User):
        pass
