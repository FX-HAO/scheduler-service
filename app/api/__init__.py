from flask.ext.restful import Api
from flask_httpauth import HTTPBasicAuth

from v1 import UserResource

auth = HTTPBasicAuth()
api = Api(prefix='/api/v1')
api.add_resource(UserResource, '/users', '/users/<int:id>', endpoint='user')
