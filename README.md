# homework
Homework for making a data pipeline to process images dataset, making queries and run models on those queries.
Requires https://www.kaggle.com/paramaggarwal/fashion-product-images-small
To reduce configuration efforts just place _fashion-dataset/_ folder into the projects _data/_ folder

Project structure:
```
.
+-- .vsode - VSCode stuff
+-- api
|   +-- __init__.py
|   +-- api.py - simple API for image query based on SQLAlchemy and batch prediction based on Pytorch
+-- celery_queue - Docker container for Celery support
|   +-- .dockerignore
|   +-- Dockerfile
|   +-- __init__.py
|   +-- requirements.txt
|   +-- tasks.py
+-- tests
|   +-- unit_test_api.py - Unit tests for API - requires data to be ingested
|   +-- unit_test_celery.py - Unit tests for Celery - requires Docker App started
+-- .gitignore
+-- README.md
+-- docker-compose.yml
+-- experiment.ipynb
+-- ingest_data_task.py
+-- init_model.py - Ensure that Fast R-CNN model is downloaded, or download otherwise
+-- requirements.txt
```

How to run:
```
> docker-compose up
# NOTE after running this I see
```
worker_1    |   File "/queue/tasks.py", line 8, in <module>
worker_1    |     from api import api
worker_1    | ModuleNotFoundError: No module named 'api'

monitor_1   |   File "/queue/tasks.py", line 8, in <module>
monitor_1   |     from api import api
monitor_1   | ModuleNotFoundError: No module named 'api'
```
If I access worker container there are no files related to api. How did you make that work?


<create virtualenv with requirements.txt in any preferrable way: Conda/pyenv/virtualenv>
> pytest tests/unit_test_celery.py
# NOTE forced to have a GPU in the machine. What would be needed to make this work with CPU as well?

> ./ingest_data_task.py
# NOTE this fails since images.csv is missing. Have you created that yourself? I didn't find it in the dataset
```
[Errno 2] No such file or directory: 'fashion-dataset/images.csv'
```

# NOTE probably `python init_model.py`?
> init_model.py

> pytest tests/unit_test_api.py
> jupyter notebook experiment.ipynb
```

Notes:
1. Installing 'psycopg2' may require additional effort in Ubuntu. This may help:
https://stackoverflow.com/questions/11583714/install-psycopg2-on-ubuntu
2. API test may require Fast R-CNN model download, which should run automatically. For this reason init_model.py script is executed before API tests.
3. Due to my GPU memory limits I can't run API tests and experiment.ipynb notebook simultaneously.


Extra comments:
- Why did you chose to use print and not a logger?
- If this would be a production system how would CI run the tests. How difficult would it be to have a one command to run all tests?
- Current setup requires local installations. How much extra work would it require to do everything inside a docker container?