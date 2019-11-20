import click
from IPython import embed


from scheduler_service.api import create_api
from scheduler_service.service import make_celery
from scheduler_service.models import create_orm

app = create_api({
    "name": "scheduler_service",
    "MODEL_URL": "postgresql://localhost/scheduler"
})
celery = make_celery(app)
create_orm(app._databases)


@click.group()
def cli():
    click.echo("START SCHEDULER SERVICE CLI")


@cli.command()
def shell():
    context = {
        "app": app
    }
    embed(user_ns=context, colors="neutral")