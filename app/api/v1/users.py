from flask_restful import Resource
from flask_restful import reqparse

from ...models import User


parser = reqparse.RequestParser()

class UserResource(Resource):
    def get(self, id):
        return User.query.get_or_404(id).json()

    def post(self):
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)
        args = parser.parse_args(strict=True)
        user = User.create(**args)
        return user.json(), 201

    def put(self, id):
        user = User.query.get_or_404(id)
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)
        args = dict((k, v) for k, v in parser.parse_args(strict=True).iteritems() if v is not None)
        user = user.update(**args)
        return user.json()

    def delete(self, id):
        User.query.get_or_404(id).delete()
        return '', 204
