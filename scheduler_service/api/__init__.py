import databases
from sanic import Sanic


def create_api(config):
    app = Sanic(name=config['name'])
    app.config.from_object(config)
    app._databases = databases.Database(config['MODEL_URL'])

    from scheduler_service.api.init_server import close_databases
    app.listeners['before_server_stop'].append(close_databases)

    return app
