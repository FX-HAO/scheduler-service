import databases
from motor import motor_asyncio
from arq import ArqRedis, create_pool
from arq.connections import RedisSettings
from sanic import Sanic
from sanic.config import Config

mongo_client: motor_asyncio.AsyncIOMotorClient = None
mongo_db: motor_asyncio.AsyncIOMotorDatabase = None
redis: ArqRedis = None
pg_db: databases.Database = None


def create_app(config):
    global pg_db
    app = Sanic(name=config.NAME)
    app.config.update_config(config)
    pg_db = databases.Database(app.config['PG_URL'])

    app.listeners['after_server_start'].extend(
        [setup_motor, setup_arq, setup_database])

    app.listeners['before_server_stop'].extend(
        [close_motor, close_arq, close_database])

    from .api.v1 import bpg
    app.blueprint(bpg)

    return app


async def setup_arq(app, loop):
    global redis
    settings = RedisSettings(
        host=app.config.get("REDIS_HOST", "localhost"),
        port=app.config.get("REDIS_PORT", 6379),
        database=app.config.get("REDIS_DATABASE", 0),
        password=app.config.get("REDIS_DATABASE", None)
    )
    redis = await create_pool(settings)


async def close_arq(app, loop):
    global redis
    redis.close()
    await redis.wait_closed()


async def setup_database(app, loop):
    await pg_db.connect()


async def close_database(app, loop):
    await pg_db.disconnect()


async def setup_motor(app, loop):
    global mongo_client, mongo_db
    mongo_client = motor_asyncio.AsyncIOMotorClient(
        "mongodb://localhost:27017", io_loop=loop)
    mongo_db = mongo_client['test']


async def close_motor(app, loop):
    global mongo_client
    mongo_client.close()


# def make_arq(config):
#     global redis
#     redis = create_pool(RedisSettings())
#     return redis
