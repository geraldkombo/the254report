from celery import Celery
from celery.schedules import crontab

from app.core.config import settings


celery_app = Celery("maji_sentinel")
celery_app.conf.broker_url = settings.redis_url
celery_app.conf.result_backend = settings.redis_url
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.enable_utc = True
celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "nightly_pipeline": {
        "task": "app.tasks.jobs.run_nightly",
        "schedule": crontab(minute=15, hour=2),
    }
}

from app.tasks import jobs as _jobs
