from flask.ext.restful import Api

from .v1 import UserResource

api = Api(prefix='/api/v1')
api.add_resource(UserResource, '/users', '/users/<int:id>', endpoint='user')
