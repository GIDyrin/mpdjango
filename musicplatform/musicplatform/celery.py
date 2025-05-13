import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'musicplatform.settings')

app = Celery('musicplatform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Использование Redis как брокера
app.conf.broker_url = "redis://redis:6379/0"  # "redis" - имя сервиса в Docker
app.conf.result_backend = "redis://redis:6379/0"