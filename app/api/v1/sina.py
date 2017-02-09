# coding: utf-8
from flask import g
from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import abort

from app.models import User, Sina
from .. import auth

parser = reqparse.RequestParser()
parser.add_argument('sina_id', type=int, help='required provide sina id')


class SinaResource(Resource):
    def get(self, id):
        user = User.get(id)
        if not user:
            abort('User is not exist')
        return user.sina.order_by(Sina.username).json()

    @auth.login_required
    def post(self):
        args = parser.parse_args(strict=True)
        sina_id = args.get('sina_id')
        sina = Sina.create(
            sina_id=sina_id,
            username="sinaSpider return value",
            follower=g.current_user
        )
        return sina.json(), 201