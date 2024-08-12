# Temperature-Prediction

[![PyPI - Python Version](https://img.shields.io/badge/python-3.10.9-blue)](https://www.python.org/downloads/)
[![Boto3](https://img.shields.io/badge/boto3-1.24-purple)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
[![Evidently](https://img.shields.io/badge/evidently-0.1.58-ec0400)](https://www.evidentlyai.com/)

[![Mage.ai](https://img.shields.io/badge/mage-2.4.2-00ad46)](https://www.mage.ai/)
[![Flask](https://img.shields.io/badge/flask-2.1.3-B2B232)](https://flask.palletsprojects.com/en/2.2.x/)
[![Matplotlib](https://img.shields.io/badge/matplotlib-3.6.1-11557c)](https://matplotlib.org/)
[![Plotly](https://img.shields.io/badge/plotly-5.10.0-7a7aff)](https://plotly.com/)
[![Seaborn](https://img.shields.io/badge/seaborn-0.12.0-333663)](https://seaborn.pydata.org/)
[![Mlflow](https://img.shields.io/badge/mlflow-1.29.0-0093e1)](https://mlflow.org/)
[![Hyperopt](https://img.shields.io/badge/hyperopt-0.2.7-35a7e7)](https://hyperopt.github.io/hyperopt/)
[![Numpy](https://img.shields.io/badge/numpy-1.23.4-013243)](https://numpy.org/)
[![Pandas](https://img.shields.io/badge/pandas-1.5.0-130654)](https://pandas.pydata.org/)
[![Psycopg2](https://img.shields.io/badge/psycopg2-2.9.4-216464)](https://pypi.org/project/psycopg2/)
[![Scikit-learn](https://img.shields.io/badge/scikit_learn-1.1.2-3399cd)](https://scikit-learn.org/)
[![Xgboost](https://img.shields.io/badge/xgboost-1.6.2-189fdd)](https://xgboost.readthedocs.io/en/stable/)
[![Black](https://img.shields.io/badge/black-22.10.0-393a39)](https://black.readthedocs.io/en/stable/)
[![Isort](https://img.shields.io/badge/isort-5.10.1-ef8336)](https://isort.readthedocs.io/en/latest/)
[![Localstack](https://img.shields.io/badge/localstack-1.2.0-2d255e)](https://localstack.cloud/)
[![Pre-commit](https://img.shields.io/badge/pre_commit-2.20.0-f8b425)](https://pre-commit.com/)
[![Pylint](https://img.shields.io/badge/pylint-2.15.4-2a5adf)](https://pylint.pycqa.org/en/latest/)
[![Pytest](https://img.shields.io/badge/pytest-7.1.3-009fe2)](https://docs.pytest.org/en/7.2.x/)
<br><br><br>


ec2-54-81-63-203.compute-1.amazonaws.com:5000

S3 bucket
mlflow-artifact-remote-1

Postgres
mlflow-backend-db


Master username  (Postgres)
mlflow
Master password (Postgres)
hob69VUuU5gxYKaPVTSS
Endpoint
mlflow-backend-db.c3omcoy2mwg1.us-east-1.rds.amazonaws.com




For the Mlops_zoomcamp final project, i choose to implement a simple solution to forecast temperature. The main goal is to apply all the skills learnt from the course. So, the emphasis will not be made on the model and the accuracy


docker build -t web_service:v1 .

docker run -it --rm -v ~/.aws:/root/.aws -p 9696:9696 web_service:v1



S3 bucket
mlflow-artifact-remote-1

Postgres
mlflow-backend-db


Master username  (Postgres)
mlflow
Master password (Postgres)
hob69VUuU5gxYKaPVTSS
Endpoint
mlflow-backend-db.c3omcoy2mwg1.us-east-1.rds.amazonaws.com




terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.50"
    }
  }
  
  backend "s3" {
  bucket = "tf-state-weather-project"
  key    = "weather-stg.tfstate"
  region = "us-east-1"
  encrypt = true
  }

  required_version = ">= 1.2.0"
}