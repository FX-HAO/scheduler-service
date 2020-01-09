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
        args = user_parse_post.parse_args(request)
        password_hash = User.hash_password(args.password)
        user = await User.objects.create(name=args.name,
                                         password_hash=password_hash,
                                         email=args.email)
        return {'uid': user.id}, 201

    async def get(self, request):
        args = user_parse_get.parse_args(request)
        if args.name:
            user = await User.objects.get(name=args.name)
        elif args.email:
            user = await User.objects.get(email=args.email)
        else:
            raise InvalidUsage("Bad Request")
        if not user.verify_password(args.password):
            raise Unauthorized("Unauthorized")
        # token = user.generate_auth_token(request.app, request.token)
        return user.to_dict()

    async def patch(self, request, user: User):
        args = user_parse_patch.parse_args(request)
        user = await user.update(**args)
        return user.to_dict()
