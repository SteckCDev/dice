from typing import Final

from celery import Celery

from infrastructure.cache.redis import RedisDatabase
from settings import settings


REDIS_DSN_WITH_DB: Final[str] = f"{settings.redis_dsn}/{RedisDatabase.CELERY.value}"

celery_instance: Celery = Celery(
    broker=REDIS_DSN_WITH_DB,
    backend=REDIS_DSN_WITH_DB,
    include=["infrastructure.queues.celery.tasks"]
)

celery_instance.conf.update(
    broker_connection_retry_on_startup=True
)
