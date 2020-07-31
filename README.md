# homework
Homework for making a data pipeline to process images dataset, making queries and run models on those queries.
Requires https://www.kaggle.com/paramaggarwal/fashion-product-images-small

Project structure:
```
.
+-- .vsode - utility VSCode stuff
+-- api
|   +-- __init__.py
|   +-- api.py - simple API for image query based on SQLAlchemy
+-- celery_queue - Docker container for Celery support
|   +-- .dockerignore
|   +-- Dockerfile
|   +-- __init__.py
|   +-- requirements.txt
|   +-- tasks.py
+-- tests
|   +-- unit_test_api.py
|   +-- unit_test_celery.py
+-- .gitignore 
+-- README.md
+-- docker-compose.yml
+-- experiment.ipynb
+-- ingest_data.py
+-- requirements.txt
```

How to run:
```
> docker-compose up
<create virtualenv with requirements.txt in any preferrable way: Conda/pyenv/virtualenv>
> ingest_data <path_to_fashion_product_dataset>
> jupyter notebook experiment.ipynb
```
Note: installing 'psycopg2' may require additional effort in Ubuntu. This may help:
https://stackoverflow.com/questions/11583714/install-psycopg2-on-ubuntu
