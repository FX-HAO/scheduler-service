from datetime import datetime
import time

import orm

from . import metadata


class User(orm.Model):
    __tablename__ = 'user'
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    name = orm.String(max_length='32')
    email = orm.String(max_length='32')
    verify = orm.Boolean(default=False)
    register_time = orm.Datetime(default=datetime.now)
    login_time = orm.Datetime()

    async def ping(self):
        await self.update(login_time=time.time())
