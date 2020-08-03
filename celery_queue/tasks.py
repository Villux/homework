import os
import time
import sys
import celery.signals
from celery import Celery
from celery.schedules import crontab
from celery.task.base import periodic_task
from api import api
import logging
import celery
from logging.config import dictConfig


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s',
             'datefmt': '%y %b %d, %H:%M:%S',
            },
        },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'celery': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'celery.log',
            'formatter': 'simple',
            'maxBytes': 1024 * 1024 * 100,  # 100 mb
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['celery', 'console'],
            'level': 'INFO',
        },
    }
}

dictConfig(LOGGING)

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@app.task(name="tasks.add")
def add(x, y):
    return x+y


@app.task(name="tasks.multiply")
def multiply(x, y):
    return x*y


@periodic_task(run_every=(crontab(minute='*')),name="run_every_minute",ignore_result=True)
def push_heart_beat():
    print ("this is heart beat")
    return "this is heart beat"


@celery.signals.setup_logging.connect  
def setup_celery_logging(**kwargs):  
    return logging.getLogger('celery') 


@app.task(name='tasks.ingest_task')
def ingest(dbURL, root_dataset_path):
    api.ingest(dbURL, root_dataset_path)
