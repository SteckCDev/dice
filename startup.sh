celery -A infrastructure.queues.celery.instance worker -P threads -l INFO -D
celery -A infrastructure.queues.celery.instance beat -s ./.periodic/celerybeat-schedule -D
python main.py
