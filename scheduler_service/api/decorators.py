from functools import wraps

from scheduler_service.models import User


def login_require(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = args[0]
        user = await User.verify_auth_token(request.app, request.token)
        return await func(*args, user=user, **kwargs)
    return wrapper
