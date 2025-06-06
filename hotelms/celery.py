import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelms.settings')

app = Celery('hotelms')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()