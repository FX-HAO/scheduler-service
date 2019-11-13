from datetime import datetime
import time

from passlib.hash import pbkdf2_sha256
import orm

from . import metadata


class User(orm.Model):
    __tablename__ = 'user'
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    name = orm.String(max_length='32')
    password_hash = orm.String(max_length='256')
    email = orm.String(max_length='32')
    verify = orm.Boolean(default=False)
    register_time = orm.DateTime(default=datetime.now)
    login_time = orm.DateTime()

    async def ping(self):
        await self.update(login_time=time.time())

    @property
    def password(self, password):
        raise AttributeError('password is not a readable attr')

    @password.setter
    def password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)
