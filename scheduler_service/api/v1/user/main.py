from sanic_restful import Resource, reqparse

from scheduler_service.api.decorators import login_require
from scheduler_service.models import User

user_parse = reqparse.RequestParser()
user_parse.add_argument("name", required=True)
user_parse.add_argument("password", required=True)
user_parse.add_argument("email", required=True)


class UserApi(Resource):
    methods = {'get': login_require}

    async def post(self, request):
        args = user_parse.parse_args(request)
        await User.objects.create(name=args.name,
                                  password=args.password,
                                  email=args.email)
        return '', 201

    async def get(self, request, user: User):
        token = user.generate_auth_token(request.app)
        return {
            "data": token
        }
