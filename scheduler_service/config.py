import json
import logging
import os
import tomllib
from datetime import datetime


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def load_config_from_toml():
    """Load configuration from config.toml if it exists."""
    config_path = os.path.join(os.getcwd(), "config.toml")
    if os.path.exists(config_path):
        try:
            with open(config_path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            print(f"Error reading config.toml: {e}")
    return {}


class Config:
    NAME = "scheduler_service"
    PG_URL = os.getenv("PG_URL", "postgres://postgres:postgres@localhost:5432/scheduler")
    SECRET_KEY = os.getenv("SECRET_KEY", 'your_secret_key')
    RESTFUL_JSON = {"cls": CustomJsonEncoder}
    LOG_LEVEL = logging.DEBUG
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    @classmethod
    def load(cls):
        """Load config from TOML and update class attributes (for backward compatibility)."""
        toml_config = load_config_from_toml()
        for k, v in toml_config.items():
            if hasattr(cls, k):
                setattr(cls, k, v)
            # Also support keys that might not be defaults but are valid
            elif k.isupper(): 
                 setattr(cls, k, v)
        return cls

    @classmethod
    def to_dict(cls):
        cls.load() # Ensure config is loaded
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('__') and not callable(v)}


# Initialize config to get current values
Config.load()

TORTOISE_ORM = {
    "connections": {"default": Config.PG_URL},
    "apps": {
        "models": {
            "models": ["scheduler_service.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
