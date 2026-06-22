import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')

# Загружаем настройки из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Явно указываем брокер и бэкенд (на случай, если они не загрузились)
app.conf.broker_url = getattr(settings, 'CELERY_BROKER_URL', 'redis://redis:6379/0')
app.conf.result_backend = getattr(settings, 'CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

app.autodiscover_tasks()