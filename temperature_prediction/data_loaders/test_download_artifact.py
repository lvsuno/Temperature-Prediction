# if 'data_loader' not in globals():
#     from mage_ai.data_preparation.decorators import data_loader
# if 'test' not in globals():
#     from mage_ai.data_preparation.decorators import test

# import os

# import mlflow
# from mlflow.tracking import MlflowClient

# EXPERIMENT_NAME = 'weather-experiment'
# TRACKING_URI = 'http://ec2-54-81-63-203.compute-1.amazonaws.com:5000'
# MODEL_NAME = 'temp-pred'

# mlflow.set_tracking_uri(TRACKING_URI)
# client = MlflowClient(tracking_uri=TRACKING_URI)


# def load_models(model_name: str, stage: str):
#     """
#     Loads the latest model saved before given the model name and stage.
#     """

#     # Get the model in the stage
#     model_stage_uri = f"models:/{model_name}/{stage}"
#     print(f"Loading registered {stage} model version from URI: {model_stage_uri}")
#     print("\n")

#     model = mlflow.pyfunc.load_model(model_stage_uri)

#     return model


# @data_loader
# def load_data(*args, **kwargs):
#     """
#     Template code for loading data from any source.

#     Returns:
#         Anything (e.g. data frame, dictionary, array, int, str, etc.)
#     """
#     # Specify your data loading logic here
#     model = load_models(MODEL_NAME, 'production')
#     if not os.path.isfile(f"{model.metadata.run_id}/dictvectorizer.bin"):
#         os.makedirs(f"{model.metadata.run_id}/")
#         relative_path = f'{model.metadata.run_id}/'
#         path = client.download_artifacts(
#             run_id=model.metadata.run_id,
#             path='models_mlflow/dictvectorizer.bin',
#             dst_path=relative_path,
#         )
#         print(f'downloading the dict vectorizer to {path}')
#         print(path)
#     return {}


# @test
# def test_output(output, *args) -> None:
#     """
#     Template code for testing the output of the block.
#     """
#     assert output is not None, 'The output is undefined'
