from sanic_restful import Resouce, reqparse

# from scheduler_service.api import 
from scheduler_service.api.decorators import login_require


class TaskApi(Resouce):
    methods = [login_require]

    async def get(self, request):
        return ''