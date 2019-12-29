import databases
from motor import motor_asyncio
from sanic import Sanic

mongo_client: motor_asyncio.AsyncIOMotorClient = None
mongo_db: motor_asyncio.AsyncIOMotorDatabase = None


def create_api(config):
    app = Sanic(name=config['name'])
    app.config.from_object(config)

    app.pg_db = databases.Database(config['PSQL_URL'])

    app.listeners['after_server_start'].append(setup_motor)

    app.listeners['bnefore_server_stop'].append(close_motor)

    from .v1 import bpg
    app.register_blueprint(bpg)


    return app

async def setup_database(app, loop):
    await app._database.connect()


async def close_database(app, loop):
    await app._databases.disconnect()


async def setup_motor(app, loop):
    global mongo_client, mongo_db
    mongo_client = motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017", io_loop=loop)
    mongo_db = mongo_client['test']


async def close_motor(app, loop):
    app.mongo_client.close()
