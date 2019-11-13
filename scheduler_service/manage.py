from scheduler_service.api import create_api
from scheduler_service.service import make_celery

app = create_api({})
celery = make_celery(app)
