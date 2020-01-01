import databases
from motor import motor_asyncio
from arq import ArqRedis, create_pool
from arq.connections import RedisSettings
from sanic import Sanic

mongo_client: motor_asyncio.AsyncIOMotorClient = None
mongo_db: motor_asyncio.AsyncIOMotorDatabase = None
redis: ArqRedis = None


def create_app(config):
    # global
    app = Sanic(name=config['name'])
    app.config.from_object(config)

    app.pg_db = databases.Database(config['PSQL_URL'])

    app.listeners['after_server_start'].extend([setup_motor, setup_arq])

    app.listeners['bnefore_server_stop'].append(close_motor)

    from .api.v1 import bpg
    app.register_blueprint(bpg)

    from .models import init_orm
    init_orm(app.pg_db)

    return app


async def setup_arq(app, loop):
    global redis
    redis = await create_pool(RedisSettings())


async def setup_database(app, loop):
    await app._database.connect()


async def close_database(app, loop):
    await app._databases.disconnect()


async def setup_motor(app, loop):
    global mongo_client, mongo_db
    mongo_client = motor_asyncio.AsyncIOMotorClient(
        "mongodb://localhost:27017", io_loop=loop)
    mongo_db = mongo_client['test']


async def close_motor(app, loop):
    app.mongo_client.close()


def make_arq(config):
    global redis
    redis = create_pool(RedisSettings())
    return redis