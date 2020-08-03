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
<create virtualenv with requirements.txt in any preferrable way: Conda/pyenv/virtualenv>
> pytest tests/unit_test_celery.py
> ./ingest_data_task.py
> init_model.py
> pytest tests/unit_test_api.py
> jupyter notebook experiment.ipynb
```

Notes: 
1. Installing 'psycopg2' may require additional effort in Ubuntu. This may help:
https://stackoverflow.com/questions/11583714/install-psycopg2-on-ubuntu
2. API test may require Fast R-CNN model download, which should run automatically. For this reason init_model.py script is executed before API tests.
3. Due to my GPU memory limits I can't run API tests and experiment.ipynb notebook simultaneously.
