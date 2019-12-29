import databases
# import motorengine
from motor import motor_asyncio
from sanic import Sanic


def create_api(config):
    app = Sanic(name=config['name'])
    app.config.from_object(config)

    app._databases = databases.Database(config['PSQL_URL'])
    app.mclient = motor_asyncio.AsyncIOMotorClient(config['MONGO_URL'])
    app.mdatabase = app.mclient[config['MONGO_DB']]
    # motorengine.connection.connect(config['MONGO_DB'], host=config['MONGO_HOST'], port=config['MONGO_PORT'])

    # from scheduler_service.api.init_server import close_database
    # app.listeners['before_server_stop'].append(close_database)

    return app
