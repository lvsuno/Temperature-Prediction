import os
import logging
from typing import Any, Dict, Tuple, Union, Optional
from datetime import datetime

import numpy as np
import mlflow
import pandas as pd
import xgboost as xgb
from mlflow import MlflowClient
from mlflow.data import from_numpy, from_pandas
from sklearn.base import BaseEstimator
from mlflow.models import infer_signature
from mlflow.xgboost import log_model as log_model_xgboost
from mlflow.entities import Run, InputTag, ViewType, DatasetInput
from mlflow.entities.model_registry.model_version_status import ModelVersionStatus

logging.getLogger("mlflow").setLevel(logging.DEBUG)
DEFAULT_DEVELOPER = os.getenv('EXPERIMENTS_DEVELOPER', 'elvis')
DEFAULT_EXPERIMENT_NAME = os.getenv('DEFAULT_EXPERIMENT_NAME', 'weather-experiment')
DEFAULT_TRACKING_URI = os.getenv(
    'DEFAULT_TRACKING_URI', 'http://ec2-54-81-63-203.compute-1.amazonaws.com:5000'
)
DEFAULT_ARTIFACT_INITIAL_PATH = os.getenv(
    'DEFAULT_ARTIFACT_INITIAL_PATH', 's3://mlflow-artifact-remote-1/'
)
DEFAULT_ARTIFACT_ROOT = os.getenv('DEFAULT_ARTIFACT_ROOT', 'models_mlflow')
MODEL_NAME = os.getenv('MODEL_NAME', 'temp-pred')


def setup_experiment(
    experiment_name: Optional[str] = None,
    tracking_uri: Optional[str] = None,
) -> Tuple[MlflowClient, str]:
    mlflow.set_tracking_uri(tracking_uri or DEFAULT_TRACKING_URI)
    experiment_name = experiment_name or DEFAULT_EXPERIMENT_NAME

    client = MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)

    if experiment:
        experiment_id = experiment.experiment_id
    else:
        experiment_id = client.create_experiment(experiment_name)

    return client, experiment_id


def track_experiment(
    experiment_name: Optional[str] = None,
    block_uuid: Optional[str] = None,
    developer: Optional[str] = None,
    hyperparameters: Dict[str, Union[float, int, str]] = {},
    metrics: Dict[str, float] = {},
    model: Optional[Union[BaseEstimator, xgb.Booster]] = None,
    partition: Optional[str] = None,
    pipeline_uuid: Optional[str] = None,
    predictions: Optional[np.ndarray] = None,
    run_name: Optional[str] = None,
    tracking_uri: Optional[str] = None,
    training_set: Optional[pd.DataFrame] = None,
    training_targets: Optional[pd.Series] = None,
    track_datasets: bool = False,
    validation_set: Optional[pd.DataFrame] = None,
    validation_targets: Optional[pd.Series] = None,
    verbosity: Union[
        bool, int
    ] = False,  # False by default or else it creates too many logs
    **kwargs,
) -> Run:
    experiment_name = experiment_name or DEFAULT_EXPERIMENT_NAME
    tracking_uri = tracking_uri or DEFAULT_TRACKING_URI

    client, experiment_id = setup_experiment(experiment_name, tracking_uri)

    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d / %H-%M-%S")

    if not run_name:
        run_name = ':'.join(
            [str(s) for s in [pipeline_uuid, partition, block_uuid] if s]
        )

        # Create an unique run_name
        run_name = f"{run_name}:{date_time}"

    run = client.create_run(experiment_id, run_name=run_name or None)
    run_id = run.info.run_id

    for key, value in [
        ('developer', developer or DEFAULT_DEVELOPER),
        ('model', model.__class__.__name__),
    ]:
        if value is not None:
            client.set_tag(run_id, key, value)

    for key, value in [
        ('block_uuid', block_uuid),
        ('partition', partition),
        ('pipeline_uuid', pipeline_uuid),
    ]:
        if value is not None:
            client.log_param(run_id, key, value)

    for key, value in hyperparameters.items():
        client.log_param(run_id, key, value)
        if verbosity:
            print(f'Logged hyperparameter {key}: {value}.')

    for key, value in metrics.items():
        client.log_metric(run_id, key, value)
        if verbosity:
            print(f'Logged metric {key}: {value}.')

    dataset_inputs = []

    # This increases memory too much.
    if track_datasets:
        for dataset_name, dataset, tags in [
            ('dataset', training_set, {"context": 'training'}),
            (
                'targets',
                training_targets.to_numpy() if training_targets is not None else None,
                {"context": 'training'},
            ),
            ('dataset', validation_set, {"context": 'validation'}),
            (
                'targets',
                (
                    validation_targets.to_numpy()
                    if validation_targets is not None
                    else None
                ),
                {"context": 'validation'},
            ),
            ('predictions', predictions, {"context": 'training'}),
        ]:
            if dataset is None:
                continue

            dataset_from = None
            if isinstance(dataset, pd.DataFrame):
                dataset_from = from_pandas
            elif isinstance(dataset, np.ndarray):
                dataset_from = from_numpy

            if dataset_from:
                ds = dataset_from(dataset, name=dataset_name)._to_mlflow_entity()
                ds_input = DatasetInput(
                    ds, tags=[InputTag(k, v) for k, v in tags.items()]
                )
                dataset_inputs.append(ds_input)

            if verbosity:
                context = tags['context']
                if dataset_from:
                    print(f'Logged input for {context} {dataset_name}.')
                else:
                    print(
                        f'Unable to log input for {context} {dataset_name}, '
                        f'{type(dataset)} not registered.'
                    )

        if len(dataset_inputs) >= 1:
            client.log_inputs(run_id, dataset_inputs)

    if model:
        log_model = None

        if isinstance(model, xgb.Booster):
            log_model = log_model_xgboost

        if log_model:
            opts = {"artifact_path": DEFAULT_ARTIFACT_ROOT, "input_example": None}

            if training_set is not None and predictions is not None:
                opts['signature'] = infer_signature(training_set, predictions)
            with mlflow.start_run(run_id=run_id) as run:
                log_model(model, **opts)
            if verbosity:
                print(f'Logged model {model.__class__.__name__}.')

    return run


def search_runs(
    client: MlflowClient, experiment_id: str, order_by: str, max_results: int = 10000
) -> list[dict]:
    """
    Searches and brings all info of the runs belonging to a specific
    experiment which is introduced to the function by its id.
    """

    runs = client.search_runs(
        experiment_ids=[experiment_id],
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=max_results,
        order_by=[order_by],
    )

    return runs


def get_best_params(
    experiment_name: Optional[str] = None,
    tracking_uri: Optional[str] = None,
    order_by: Optional[str] = "metrics.rmse ASC",
    max_results: int = 10000,
) -> tuple[dict[str, Any], str]:
    """
    Gets the parameters of the best model run of a particular experiment.
    """
    experiment_name = experiment_name or DEFAULT_EXPERIMENT_NAME
    tracking_uri = tracking_uri or DEFAULT_TRACKING_URI

    client, experiment_id = setup_experiment(experiment_name, tracking_uri)

    # Get the pandas data frame of the experiment results in the ascending order by RMSE
    runs = search_runs(client, experiment_id, order_by, max_results)

    # Get the id of the best run
    best_run_id = runs[0].info.run_id

    # Get the best model parameters
    best_params = runs[0].data.params
    rmse = runs[0].data.metrics["rmse"]
    print("\n")
    print(
        f"Best parameters from the run {best_run_id} of '{experiment_id}/{experiment_name}':"
    )
    print("\n")
    print("rmse:", rmse)
    for key, value in best_params.items():
        print(f"{key}: {value}")
    print("\n")

    best_params.pop('block_uuid')
    best_params.pop('pipeline_uuid')

    return best_params


def register_model(
    best_run_id: str,
    artifact_path: Optional[str] = None,
    model_name: Optional[str] = None,
) -> dict[str, Any]:
    """
    Registers the model.
    """
    artifact_path = artifact_path or DEFAULT_ARTIFACT_ROOT

    model_name = model_name or MODEL_NAME
    # Register the model
    model_uri = f"runs:/{best_run_id}/{artifact_path}"
    model_details = mlflow.register_model(model_uri=model_uri, name=model_name)
    mlflow.log_artifacts(
        'data/Training/DictVect/', artifact_path=artifact_path, run_id=best_run_id
    )
    print("/n")
    print(
        f"Version {model_details.version} of the model {model_details.name} has been registered."
    )
    print("\n")
    print("Model details:", "\n", model_details, "\n")

    return model_details


def wait_until_ready(
    model_name: Optional[str] = None, model_version: Optional[str] = None
):
    """
    After creating a model version, it may take a short period of time to become ready.
    Certain operations, such as model stage transitions, require the model to be in the
    READY state. Other operations, such as adding a description or fetching model details,
    can be performed before the model version is ready (for example, while it is in the
    PENDING_REGISTRATION state).

    Uses the MlflowClient.get_model_version() function to wait until the model is ready.
    """

    client, _ = setup_experiment(DEFAULT_EXPERIMENT_NAME, DEFAULT_TRACKING_URI)
    model_name = model_name or MODEL_NAME

    status = "Not ready"

    while status == "Not ready":

        model_version_details = client.get_model_version(
            name=model_name,
            version=model_version,
        )

        status = ModelVersionStatus.from_string(model_version_details.status)
        print(f"Model status: {ModelVersionStatus.to_string(status)}")
        print("\n")
        print(f"Model {model_name} is ready for further processing.")
    return client


def update_registered_model(
    client: MlflowClient, model_name: str, description: str
) -> str:
    """
    Adds a description to the model.
    """

    # client, _ = setup_experiment(DEFAULT_EXPERIMENT_NAME, DEFAULT_TRACKING_URI)
    response = client.update_registered_model(name=model_name, description=description)

    mod_name = response.name

    print(f"Description has been added to the model {model_name}.")
    print("\n")

    return mod_name


def update_model_version(
    client: MlflowClient, model_name: str, model_version: str, version_description: str
) -> str:
    """
    Adds a description to a version of the model.
    """

    response = client.update_model_version(
        name=model_name, version=model_version, description=version_description
    )

    run_id = response.run_id

    print(
        f"Description has been added to the version {model_version} of the model {model_name}."
    )
    print("\n")

    return run_id


def transition_to_stage(
    client: MlflowClient,
    model_name: str,
    model_version: str,
    new_stage: str,
    archive: bool,
) -> None:
    """
    Transitions a model to a defined stage.
    """

    # Transition the model to the stage
    client.transition_model_version_stage(
        name=model_name,
        version=model_version,
        stage=new_stage,
        archive_existing_versions=archive,
    )

    print(
        f"Version {model_version} of the model {model_name} has been transitioned to {new_stage}."
    )
    print("\n")


def load_models(model_name: str, stage: str) -> Any:
    """
    Loads the latest model saved before given the model name and stage.
    """

    # Get the model in the stage
    model_stage_uri = f"models:/{model_name}/{stage}"
    print(f"Loading registered {stage} model version from URI: {model_stage_uri}")
    print("\n")

    model = mlflow.pyfunc.load_model(model_stage_uri)

    return model


def get_latest_version(client: MlflowClient, model_name: str, stage: str) -> str:
    """
    Finds the version number of the latest version of a model in a particular stage.
    """

    # Get the information for the latest version of the model in a given stage
    latest_version_info = client.get_latest_versions(model_name, stages=[stage])
    latest_stage_version = latest_version_info[0].version

    print(
        f"The latest {stage} version of the model {model_name} is {latest_stage_version}."
    )
    print("\n")

    return latest_stage_version


def delete_version(client: MlflowClient, model_name: str, model_version: int) -> None:
    """
    Deletes a specific version of a model permanently.
    """

    client.delete_model_version(
        name=model_name,
        version=model_version,
    )

    print(
        f"The version {model_version} of the model {model_name} has been permanently deleted."
    )
    print("\n")
