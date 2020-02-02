from datetime import datetime

import orm

from scheduler_service import pg_db
from . import metadata
from .mixin import CRUDMixin


class Task(orm.Model, CRUDMixin):
    __tablename__ = 'task'
    __metadata__ = metadata
    __database__ = pg_db

    id = orm.Integer(primary_key=True)
    name = orm.String(max_length=32)
    interval = orm.Integer(allow_null=True)
    start_time = orm.DateTime(default=datetime.utcnow)
    cookies = orm.JSON(allow_null=True)

    user_id = orm.Integer()


    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.interval,
            "start_time": self.start_time,
            "cookies": self.cookies
        }    


class URLDetail(orm.Model, CRUDMixin):
    __tablename__ = 'url_detail'
    __metadata__ = metadata
    __database__ = pg_db

    id = orm.Integer(primary_key=True)
    name = orm.String(max_length=32)
    request_url = orm.String(max_length=128)
    callback_url = orm.String(max_length=128)
    params = orm.JSON()

    task_id = orm.Integer()

# class Response(Document):
#     time = DateTimeField(default=datetime.now)
#     body = JsonField()
