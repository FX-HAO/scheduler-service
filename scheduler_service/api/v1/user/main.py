from sanic.exceptions import InvalidUsage, Unauthorized
from sanic_restful import Resource, reqparse

from scheduler_service.api.decorators import login_require
from scheduler_service.models import User

user_parse_post = reqparse.RequestParser()
user_parse_post.add_argument("name", required=True)
user_parse_post.add_argument("password", required=True)
user_parse_post.add_argument("email", required=True)

user_parse_get = reqparse.RequestParser()
user_parse_get.add_argument("name")
user_parse_get.add_argument("email")
user_parse_get.add_argument("password", required=True)


class UserApi(Resource):

    async def post(self, request):
        params = user_parse_post.parse_args(request)
        await User.objects.create(name=params.name,
                                  password=params.password,
                                  email=params.email)
        return '', 201

    async def get(self, request):
        params = user_parse_get.parse_args(request)
        if params.name:
            user = await User.objects.filter(name=params.name)
        elif params.email:
            user = await User.objects.filter(email=params.email)
        else:
            raise InvalidUsage("Bad Request")
        if not user.verify_password(params.password):
            raise Unauthorized("Unauthorized")
        token = user.generate_auth_token(request.app, request.token)
        return {
            "data": token
        }
