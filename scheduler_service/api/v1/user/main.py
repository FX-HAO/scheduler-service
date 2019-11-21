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

user_parse_patch = reqparse.RequestParser()
user_parse_patch.add_argument("name")
user_parse_patch.add_argument("email")
user_parse_patch.add_argument("password")


class UserApi(Resource):
    methods = {"get": login_require}

    async def post(self, request):
        params = user_parse_post.parse_args(request)
        password_hash = User.hash_password(params.password)
        await User.objects.create(name=params.name,
                                  password_hash=password_hash,
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
        # token = user.generate_auth_token(request.app, request.token)
        return user.to_dict()

    async def patch(self, request, user: User):
        params = user_parse_patch.parse_args(request)
        user = await user.update(**params)
        return user.to_dict()
