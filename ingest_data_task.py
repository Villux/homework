#!/usr/bin/env python3

import sys
import os
from api import api
from celery import chain
from celery_queue import tasks

if __name__ == "__main__":
    if len(sys.argv) > 1:
        root_dataset_path = sys.argv[1]
    else:
        root_dataset_path = 'fashion-dataset'

    # task = tasks.ingest.apply_async(args=[api.DB_URL, root_dataset_path])    
    # print(task)

    # sync apply to show progress messages
    # Unfortunately, I failed to setup proper logging
    tasks.ingest.apply(args=[api.DB_URL, root_dataset_path])    
