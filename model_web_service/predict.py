import os

import model
from flask import Flask, jsonify, request

MODEL_NAME = os.getenv('MODEL_NAME', 'temp-pred')
TEST_RUN = os.getenv("TEST_RUN", "False") == "True"
MODEL_STAGE = os.getenv('MODEL_STAGE', 'Production')


model_service = model.init(
    model_name=MODEL_NAME, model_stage='Production', test_run=TEST_RUN
)

# initialize flask application

app = Flask('temperature-prediction')


# for health check
@app.route('/health', methods=['GET'])
def check_health():

    return "OK", 200


# create endpoint
@app.route('/predict', methods=['POST'])
def predict_endpoint():

    data = request.get_json()

    return jsonify(model_service.inference(data))


# only app is run when script is called directly
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
