import os
import pickle
from datetime import datetime

import mlflow
from flask import Flask, jsonify, request
from mlflow.tracking import MlflowClient

EXPERIMENT_NAME = 'weather-experiment'
TRACKING_URI = 'http://ec2-54-81-63-203.compute-1.amazonaws.com:5000'
ARTIFACT_INITIAL_PATH = 's3://mlflow-artifact-remote-1/'
ARTIFACT_ROOT = 'models_mlflow'
MODEL_NAME = 'temp-pred'


# RUN_ID = dotenv_values(".env")['RUN_ID']
# RUN_ID = os.getenv('RUN_ID')
# MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"

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


# preprocess data
def prepare_features(data):
    features = {}
    datetime_object = datetime.strptime(data['Date/Time (LST)'], '%Y-%m-%d %H:%M:%S')
    features['Station ID'] = str(data['Station ID'])
    features['Date_Time_Num'] = datetime_object.timestamp()
    return features


model = load_models(MODEL_NAME, 'production')

if not os.path.isfile(f"{model.metadata.run_id}/dictvectorizer.bin"):
    os.makedirs(f"{model.metadata.run_id}/")
    relative_path = f'{model.metadata.run_id}/'
    path = client.download_artifacts(
        run_id=model.metadata.run_id,
        path='models_mlflow/dictvectorizer.bin',
        dst_path=relative_path,
    )
    os.environ['run_id'] = model.metadata.run_id
    print(f'downloading the dict vectorizer to {path}')
    with open(path, 'rb') as f_in:
        dv = pickle.load(f_in)
else:
    with open(f"{model.metadata.run_id}/dictvectorizer.bin", 'rb') as f_in:
        dv = pickle.load(f_in)


# # genrate prediction
def predict(features):
    X = dv.transform(features)
    preds = model.predict(X)
    return float(preds[0])


# initialize flask application

app = Flask('temperature-prediction')


# create endpoint
@app.route('/predict', methods=['POST'])
def predict_endpoint():

    data = request.get_json()

    features = prepare_features(data)

    pred = predict(features)

    result = {'prediction': pred, 'Model RUN_ID': model.metadata.run_id}

    return jsonify(result)


# only app is run when script is called directly
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
