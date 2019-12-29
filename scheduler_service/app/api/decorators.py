from functools import wraps

from sanic.exceptions import Unauthorized

from scheduler_service.app.models import User


def login_require(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = args[0]
        user = await User.verify_auth_token(request.app, request.token)
        if not user:
            raise Unauthorized("Unauthorized")
        return await func(*args, user=user, **kwargs)
    return wrapper
