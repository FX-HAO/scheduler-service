from sanic.exceptions import InvalidUsage, Unauthorized
from sanic_restful import Resource, reqparse

from scheduler_service.api.decorators import login_require
from scheduler_service.models import User

user_parse_post = reqparse.RequestParser()
user_parse_post.add_argument("name", required=True)
user_parse_post.add_argument("password", required=True)
user_parse_post.add_argument("email", required=True)

user_parse_patch = reqparse.RequestParser()
user_parse_patch.add_argument("name", store_missing=False)
user_parse_patch.add_argument("email", store_missing=False)
user_parse_patch.add_argument("password", store_missing=False)


class UserApi(Resource):
    method_decorators = {
        "get": login_require,
        "patch": login_require,
        "delete": login_require
    }

    async def post(self, request):
        args = user_parse_post.parse_args(request)
        password_hash = User.hash_password(args.password)
        user = await User.objects.create(name=args.name,
                                         password_hash=password_hash,
                                         email=args.email)
        return {'uid': user.id}, 201

    async def get(self, request, user: User):
        return user.to_dict()

    async def patch(self, request, user: User):
        args = user_parse_patch.parse_args(request)
        await user.update(**args)
        return user.to_dict()

    async def delete(self, request, user: User):
        await user.delete()
