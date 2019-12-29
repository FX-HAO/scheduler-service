import click
from IPython import embed
import databases
import orm
import sqlalchemy


from scheduler_service.api import create_api
from scheduler_service.service import make_celery
from scheduler_service.models import init_orm, User

app = create_api({
    "name": "scheduler_service",
    "PSQL_URL": "postgresql://localhost/scheduler",
    "MONGO_URL": "mongodb://localhost:27017",
    "MONGO_DB": "test"
})
celery = make_celery(app)
init_orm(app.pg_db)


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