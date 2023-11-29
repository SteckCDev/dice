pip install -r requirements.txt
alembic upgrade head

celery -A infrastructure.queues.celery.instance worker -P threads -l INFO --detach
celery -A infrastructure.queues.celery.instance beat -s ./.periodic/celerybeat-schedule --detach
