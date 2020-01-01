import asyncio

import click
from IPython import embed

from scheduler_service import create_app, redis
from scheduler_service.models import User

app = create_app({
    "name": "scheduler_service",
    "PSQL_URL": "postgresql://localhost/scheduler",
    "MONGO_URL": "mongodb://localhost:27017",
    "MONGO_DB": "test"
})


@click.group()
def cli():
    click.echo("START SCHEDULER SERVICE CLI")


@cli.command()
def shell():
    context = {
        "app": app,
        "User": User
    }
    embed(user_ns=context,
          colors="neutral",
          using="asyncio",
          header="First: await app._database.connect()")


@cli.command()
@click.option("--host", default="localhost")
@click.option("--port", default=8080)
def runserver(host, port):
    app.run(debug=True, host=host, port=port)


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
