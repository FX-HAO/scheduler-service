from datetime import datetime
import time

import orm

from . import metadata


class User(orm.Model):
    __tablename__ = 'user'
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    name = orm.String(max_length='32')
    password_hash = orm.String(max_length='128')
    email = orm.String(max_length='32')
    verify = orm.Boolean(default=False)
    register_time = orm.DateTime(default=datetime.now)
    login_time = orm.DateTime()

    async def ping(self):
        await self.update(login_time=time.time())
