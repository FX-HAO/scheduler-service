from datetime import datetime
import time

import jwt
from passlib.hash import pbkdf2_sha256
import orm

from . import metadata
from .mixin import CRUDMixin


class User(orm.Model, CRUDMixin):
    __tablename__ = 'user'
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    name = orm.String(max_length=32)
    password_hash = orm.String(max_length=256)
    email = orm.String(max_length=32)
    verify = orm.Boolean(default=False)
    register_time = orm.DateTime(default=datetime.now)
    login_time = orm.DateTime(allow_null=True)

    async def ping(self):
        await self.update(login_time=time.time())

    # @property
    # def password(self, password):
    #     raise AttributeError('password is not a readable attr')

    # @password.setter
    @staticmethod
    def hash_password(password):
        return pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

    def generate_auth_token(self, app) -> str:
        return jwt.encode({'id': self.id, 'flag': 'auth'},
                          app.config['SECRET_KEY'],
                          algorithm='HS256')

    @classmethod
    async def verify_auth_token(cls, app, token: str) -> bool:
        try:
            data = jwt.decode(token,
                              app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except Exception:
            return False
        else:
            if data['flag'] != 'auth':
                return False
            return await cls.objects.get(id=data['id'])

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }
