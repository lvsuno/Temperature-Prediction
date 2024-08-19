import model


def test_prepare_features():
    model_service = model.ModelService(None)
    datetime_str = '2024-08-09 23:00:00'

    data = {"Station ID": 50840, "Date/Time (LST)": datetime_str}

    actual_features = model_service.prepare_features(data)

    expected_features = {
        "Station ID": "50840",
        "Date_Time_Num": 1723258800.0,
    }

    assert actual_features == expected_features


class ModelMock:
    def __init__(self, value):
        self.value = value

    def predict(self, X):
        n = len(X)
        return [self.value] * n


def test_predict():

    # To make the test the most independant possible
    # SO we don't need to go to S3 and download the model
    model_mock = ModelMock(10.0)
    model_service = model.ModelService(model_mock)

    features = {
        "Station ID": "50840",
        "Date_Time_Num": 1723258800.0,
    }

    actual_prediction = model_service.predict(features)
    expected_prediction = 10

    assert actual_prediction == expected_prediction


def test_inference():
    model_mock = ModelMock(10)
    model_service = model.ModelService(model_mock)
    datetime_str = '2024-08-09 23:00:00'

    data = {"Station ID": 50840, "Date/Time (LST)": datetime_str}

    actual_predictions = model_service.inference(data)

    expected_predictions = {'prediction': 10}

    assert actual_predictions == expected_predictions
