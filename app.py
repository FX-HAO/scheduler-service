from flask import Flask, Blueprint
from flask_restful import Resource, Api

from resources.spider import api_spider

app = Flask(__name__)
api = Api(app)

class Index(Resource):
    def get(self):
        return "Hello, World", 201

api.add_resource(Index, '/index', endpoint='index')
app.register_blueprint(api_spider, url_prefix='/spider')

if __name__ == '__main__':
    app.run(debug=True)