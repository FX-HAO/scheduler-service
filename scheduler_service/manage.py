import click
from IPython import embed
import os
import sys
sys.path.insert(0, ".")
env = os.getenv("schedulerEnv", "default")

from sanic.log import logger

from scheduler_service import create_app
try:
    import config
except ImportError:
    from scheduler_service.config import configs
    config = configs.get(env)

app = create_app(config)
from scheduler_service import pg_db
from scheduler_service.models import User


@click.group()
def cli():
    click.echo("START SCHEDULER SERVICE CLI")


@cli.command()
def shell():
    context = {
        "app": app,
        "User": User,
        "pg_db": pg_db
    }
    embed(user_ns=context,
          colors="neutral",
          using="asyncio",
          header="First: await app._database.connect()")


@cli.command()
@click.option('-h', "--host", default="localhost")
@click.option('-p', "--port", default=8080, type=int)
@click.option('-w', "--works", default=1, type=int)
@click.option('--debug/--no-debug', default=True)
@click.option('--access-log/--no-access-log', default=True)
def runserver(host, port, works, debug, access_log):
    app.run(debug=debug,
            host=host,
            port=port,
            workers=works,
            access_log=access_log)


@cli.command()
@click.option('--check',
              is_flag=True,
              help='Health Check: run a health check and exit.')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose output.')
def arq(check, verbose):
    import logging

    from arq.logs import default_log_config
    from arq.worker import check_health, run_worker

    from scheduler_service.service import WorkerSettings
    logging.config.dictConfig(default_log_config(verbose))

    if check:
        exit(check_health(WorkerSettings))
    else:
        kwargs = {}
        run_worker(WorkerSettings, **kwargs)


@cli.command()
def init_db():
    import sqlalchemy
    from scheduler_service.models import metadata
    engine = sqlalchemy.create_engine(str(pg_db.url))
    metadata.create_all(engine)
