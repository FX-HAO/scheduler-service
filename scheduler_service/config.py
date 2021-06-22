from datetime import datetime
import json


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class Config:
    NAME = "scheduler_service"
    PG_URL = "postgresql://localhost/scheduler"
    MONGO_URL = "mongodb://localhost:27017"
    MONGO_DB = "test"
    SECRET_KEY = '64697a5d-53de-476e-b9ed-5f9851bfa4c4'
    MAX_TASKS = 10
    RESTFUL_JSON = {"cls": CustomJsonEncoder}

    @classmethod
    def to_dict(cls):
        return dict(cls.__dict__)

class TestConfig(Config):
    PG_URL = "postgresql://localhost/scheduler_test"


configs = {
    "default": Config,
    "test": TestConfig
}
