import click
from IPython import embed

from scheduler_service.app import create_api
from scheduler_service.app.models import User

app = create_api({
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