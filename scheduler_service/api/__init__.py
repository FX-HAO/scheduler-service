import databases
# import motorengine
from motor import motor_asyncio
from sanic import Sanic

# mongo_client: motor_asyncio.AsyncIOMotorClient = None
# mongo_db: motor_asyncio.AsyncIOMotorDatabase = None

def create_api(config):
    # global mongo_client, mongo_db
    app = Sanic(name=config['name'])
    app.config.from_object(config)

    app.pg_db = databases.Database(config['PSQL_URL'])

    # app.mongo_client = motor_asyncio.AsyncIOMotorClient(config['MONGO_URL'])
    # app.mongo_client = mongo_client
    # app.mongo_db = app.mongo_client[config['MONGO_DB']]
    # app.mongo_db = mongo_db 
    # motorengine.connection.connect(config['MONGO_DB'], host=config['MONGO_HOST'], port=config['MONGO_PORT'])

    from scheduler_service.api.init_server import setup_motor
    app.listeners['after_server_start'].append(setup_motor)
    # from scheduler_service.api.init_server import close_database
    # app.listeners['before_server_stop'].append(close_database)

    from .v1 import bpg
    app.register_blueprint(bpg)


    return app
