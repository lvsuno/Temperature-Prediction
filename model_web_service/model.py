"""
Code for evrything refering to the model
"""

import os
import pickle
from typing import Optional
from datetime import datetime

# import boto3  # type: ignore
import mlflow
from mlflow.tracking import MlflowClient

EXPERIMENT_NAME = 'weather-experiment'
TRACKING_URI = 'http://ec2-54-81-63-203.compute-1.amazonaws.com:5000'
ARTIFACT_INITIAL_PATH = 's3://mlflow-artifact-remote-1/'
ARTIFACT_ROOT = 'models_mlflow'
MODEL_NAME = 'temp-pred'


mlflow.set_tracking_uri(TRACKING_URI)

client = MlflowClient(tracking_uri=TRACKING_URI)


def load_models(model_name: str, stage: str):
    """
    Loads the latest model saved before given the model name and stage.
    """

    # Get the model in the stage
    model_stage_uri = f"models:/{model_name}/{stage}"
    print(f"Loading registered {stage} model version from URI: {model_stage_uri}")
    print("\n")

    model1 = mlflow.pyfunc.load_model(model_stage_uri)

    return model1


def retrieve_dict(model):
    if not os.path.isfile(f"model_{model.metadata.run_id}/dictvectorizer.bin"):
        os.makedirs(f"model_{model.metadata.run_id}/")
        relative_path = f'model_{model.metadata.run_id}/'
        path = client.download_artifacts(
            run_id=model.metadata.run_id,
            path='models_mlflow/dictvectorizer.bin',
            dst_path=relative_path,
        )
        # os.environ['run_id'] = model.metadata.run_id
        print(f'downloading the dict vectorizer to {path}')
        with open(path, 'rb') as f_in:
            dv = pickle.load(f_in)
    else:
        with open(f"model_{model.metadata.run_id}/dictvectorizer.bin", 'rb') as f_in:
            dv = pickle.load(f_in)
    return dv


class ModelService:

    def __init__(self, model, dv=None, model_version=None):
        self.model = model
        self.dv = dv
        self.model_version = model_version

    def prepare_features(self, data):
        features = {}
        datetime_object = datetime.strptime(
            data["Date/Time (LST)"], '%Y-%m-%d %H:%M:%S'
        )
        features['Station ID'] = str(data['Station ID'])
        features['Date_Time_Num'] = datetime_object.timestamp()
        return features

    def predict(self, features):
        if self.dv:
            X = self.dv.transform(features)
        else:
            X = features
        pred = self.model.predict(X)
        return int(pred[0])

    def inference(self, data):

        features = self.prepare_features(data)
        prediction = self.predict(features)
        result = {'prediction': prediction}
        return result


def init(
    model_name: str,
    model_stage: str,
    test_run: bool = False,
    model_version: Optional[str] = None,
):

    if not test_run:
        model = load_models(model_name, model_stage)
        dictionary = retrieve_dict(model)
    else:
        model = mlflow.pyfunc.load_model("model/")
        with open("model/dictvectorizer.bin", 'rb') as f_in:
            dictionary = pickle.load(f_in)

    model_service = ModelService(
        model=model, dv=dictionary, model_version=model_version
    )

    return model_service
