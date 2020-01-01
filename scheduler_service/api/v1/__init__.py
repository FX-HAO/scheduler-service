from sanic import Blueprint

from .task import bp as task_bp
from .user import bp as user_bp

bpg = Blueprint.group(task_bp, user_bp, url_prefix="v1")
