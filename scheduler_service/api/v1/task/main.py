from datetime import datetime

from bson import ObjectId
from sanic.request import Request
from sanic.exceptions import InvalidUsage
from sanic_restful import Resource, reqparse

from scheduler_service import mongo_db
from scheduler_service.api.decorators import login_require
from scheduler_service.models import User, Task, URLDetail


tasks_post_parse = reqparse.RequestParser()
tasks_post_parse.add_argument("name", required=True)
tasks_post_parse.add_argument("interval", type=int)
tasks_post_parse.add_argument("start_time", type=int)
tasks_post_parse.add_argument("cookies")

task_parse = reqparse.RequestParser()
task_parse.add_argument("request_url", required=True)
task_parse.add_argument("callback_url")
task_parse.add_argument("name")
task_parse.add_argument("params")


class TasksApi(Resource):
    decorators = [login_require]

    async def get(self, request: Request, user: User):
        tasks = await Task.objects.filter(uid=User.id).all()
        return {
            "tasks": tasks
        }

    async def post(self, request: Request, user: User):
        tasks = await Task.objects.filter(uid=User.id).all()
        if len(tasks) >= request.app.config['MAX_TASKS']:
            raise InvalidUsage("NUMBER OF TASKS EXCEEDS THE LIMIT")

        params = tasks_post_parse.parse_args(request)
        task = await Task.objects.create(
            name=params.name,
            interval=params.interval,
            user_id=user.id,
            start_time=datetime.fromtimestamp(params.start_time)
        )
        return {
            'task_id': task.id
        }


class TaskApi(Resource):
    decorators = [login_require]

    async def get(self, request: Request, user: User, task_id: int):
        tasks = await Task.objects.filter(user_id=user.id).all()
        return {
            'tasks': [t.to_dict() for t in tasks]
        }

    async def post(self, request: Request, user: User, task_id: int):
        urls = await URLDetail.objects.filter(id=task_id)
        if len(urls) >= request.app.config['MAX_URLS']:
            raise InvalidUsage("NUMBER OF URLS EXCEEDS THE LIMIT")
        params = task_parse.parse_args(request)
        url_detail = await URLDetail.objects.create(
            request_url=params.request_url,
            callback_url=params.callback_url,
            name=params.name,
            params=params.params,
            task_id=task_id)
        return {
            'url_id': url_detail
        }

    async def delete(self, request: Request, user: User, task_id: int):
        task = await Task.objects.get(id=task_id)
        await task.delete()

    async def patch(self, request: Request, user: User):
        pass
