import os
import time
import sys
from celery import Celery
from celery.schedules import crontab
from celery.task.base import periodic_task

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery.task(name="tasks.add")
def add(x, y):
    return x+y

@celery.task(name="tasks.multiply")
def multiply(x, y):
    return x*y
