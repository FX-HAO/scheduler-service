from aiohttp import ClientSession

from .request import ping

# # def make_celery(app: Sanic) -> Celery:
# #     celery = Celery(app.name)
# #     celery.conf.update(app.config)
# #     return celery


# async def make_arq():
#     return await create_pool(RedisSettings())


async def startup(ctx):
    ctx['session'] = ClientSession()


async def shutdown(ctx):
    await ctx['session'].close()


class WorkerSettings:
    functions = [ping]
    on_startup = startup
    on_shutdown = shutdown
