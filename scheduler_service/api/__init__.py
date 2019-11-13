from sanic import Sanic


def create_api(config):
    app = Sanic()
    app.config.from_object(config)

    from scheduler_service.api.init_server import (setup_databases,
                                                   close_databases)

    app.listeners['before_server_start'].append(setup_databases)
    app.listeners['before_server_stop'].append(close_databases)

    return app
