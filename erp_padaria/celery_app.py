# erp_padaria/celery_app.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_padaria.settings')

app = Celery('erp_padaria')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()