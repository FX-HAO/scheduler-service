from flask import Flask, Blueprint
from flask_restful import Resource, Api, abort, reqparse

api_spider = Blueprint('spider', __name__)
api = Api(api_spider)

parser = reqparse.RequestParser()
parser.add_argument("sina_id", type=int, required=True, help="Required int")

class SinaSpider(Resource):
    def post(self):
        args = parser.parse_args()
        sina_id = args["sina_id"]
        "doing something"
        return sina_id, 201

api.add_resource(SinaSpider, '/sina', endpoint="SinaSpider")
