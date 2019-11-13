from sanic import Sanic


def create_api(config):
    app = Sanic()
    app.config.from_object(config)
