from sanic import Blueprint

from .task import bp

bpg = Blueprint.group(bp, url_prefix="v1")
