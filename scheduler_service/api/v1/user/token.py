from sanic.exceptions import InvalidUsage, Unauthorized
from sanic_restful import Resource, reqparse

from scheduler_service.models import User


parser = reqparse.RequestParser()
parser.add_argument("name")
parser.add_argument("email")
parser.add_argument("password", required=True)


class AuthTokenApi(Resource):

    async def get(self, request):
        args = parser.parse_args(request)
        if args.name:
            user = await User.objects.get(name=args.name)
        elif args.email:
            user = await User.objects.get(email=args.email)
        else:
            raise InvalidUsage("Input Username or Email, Please")
        if user.verify_password(args.password):
            raise Unauthorized("Username or Password is incorrect")

        return {
            "token": user.generate_auth_token(request.app)
        }
