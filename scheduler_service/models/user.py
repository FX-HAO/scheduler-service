from datetime import datetime

import jwt
from passlib.hash import pbkdf2_sha256
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model

from scheduler_service.utils.logger import logger


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32, unique=True)
    password_hash = fields.CharField(max_length=256)
    email = fields.CharField(max_length=32, unique=True)
    verify = fields.BooleanField(default=False)
    register_time = fields.DatetimeField(auto_now_add=True)
    login_time = fields.DatetimeField(null=True)

    async def ping(self):
        self.login_time = datetime.now()
        await self.save()

    @property
    def password(self):
        raise AttributeError('password is not a readable attr')

    @password.setter
    def password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pbkdf2_sha256.hash(password)

    def verify_password(self, password: str) -> bool:
        return pbkdf2_sha256.verify(password, self.password_hash)

    def generate_auth_token(self, secret_key: str) -> str:
        return jwt.encode({'id': self.id, 'flag': 'auth'},
                          secret_key,
                          algorithm='HS256')

    @classmethod
    async def verify_auth_token(cls, token: str, secret_key: str):
        # Temporary print for debugging
        print(f"DEBUG: verify_auth_token received secret_key: {secret_key}")
        try:
            data = jwt.decode(token,
                              secret_key,
                              algorithms=['HS256'])
        except Exception as e:
            logger.debug(f"Token verification error (jwt.decode): {e}")
            return False
        else:
            if data['flag'] != 'auth':
                logger.debug("Token verification error: Invalid flag")
                return False
            try:
                return await cls.get(id=data['id'])
            except DoesNotExist:
                logger.debug("Token verification error: User does not exist for ID")
                return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }
