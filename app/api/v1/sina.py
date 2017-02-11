# coding: utf-8
from flask import g
from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import abort
import requests

from app.models import User, Sina
from .. import auth

parser = reqparse.RequestParser()
parser.add_argument('sina_user_url', type=str, help='required provide sina url')


class SinaResource(Resource):
    def get(self, id):
        user = User.get(id)
        if not user:
            abort('User is not exist')
        return user.sina.order_by(Sina.username).json()

    @auth.login_required
    def post(self):
        args = parser.parse_args(strict=True)
        sina_url = args.get('sina_user_url')
        response = requests.get(url=sina_url)
        if response.status_code != 200:
            abort('sina user is not exist')
        sina_id = "return sina user id"
        sina_username = "return sina username"
        sina = Sina.create(
            sina_id=sina_id,
            username=sina_username,
            follower=g.current_user
        )
        return sina.json(), 201