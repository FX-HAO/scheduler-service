from scheduler_service.api import create_api
from scheduler_service.service import make_celery
from scheduler_service.models import create_orm

app = create_api({})
celery = make_celery(app)
create_orm(app._databases)
