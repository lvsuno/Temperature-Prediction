if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

import os
from typing import Dict, Tuple, Union

from mlflow import MlflowClient
from pandas import Series
from xgboost import Booster
from sklearn.metrics import mean_squared_error
from scipy.sparse._csr import csr_matrix
from mage_ai.data_preparation.variable_manager import set_global_variable

from temperature_prediction.utils.logging import (
    load_models,
    delete_version,
    register_model,
    get_best_params,
    setup_experiment,
    track_experiment,
    wait_until_ready,
    get_latest_version,
    transition_to_stage,
    update_model_version,
    update_registered_model,
)
from temperature_prediction.utils.models.xgboost import build_data


@data_exporter
def test_and_compare(
    settings: Tuple[
        Dict[str, Union[bool, float, int, str]],
        Union[Series, csr_matrix],
    ],
    staging_data: Tuple[
        Booster,
        float,
        Series,
        str,
    ],
    *args,
    **kwargs,
):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    _, X_train, X_val, y_train, y_val = settings

    training = build_data(X_train, y_train)
    validation = build_data(X_val, y_val)

    (
        model_staging,
        model_staging_rmse,
        model_staging_predictions,
        model_staging_version,
    ) = staging_data

    model_name = os.getenv('MODEL_NAME') or kwargs.get('MODEL_NAME')

    try:
        # Load the production model, predict with the new data and calculate its RMSE
        model_production = load_models(model_name, "Production")
        model_production_predictions = model_production.predict(X_val)

        model_production_rmse = mean_squared_error(
            validation.get_label(), model_production_predictions, squared=False
        )
        print("model_production_rmse: %s", model_production_rmse)

    except Exception:
        print(
            "It seems that there is not any model in the production stage yet. \
                Then, we transition the current model to production."
        )
        model_production_rmse = None

    if model_production_rmse:
        set_global_variable(
            'training', 'model_production_rmse', str(model_production_rmse)
        )
    set_global_variable('training', 'model_staging_rmse', str(model_staging_rmse))

    # Compare model
    client, _ = setup_experiment()
    if model_production_rmse:
        print(model_production_rmse)

        # If the staging model's RMSE is lower than or equal to the production model's
        # RMSE, transition the former model to production stage, and delete the previous
        # production model.
        if model_staging_rmse <= model_production_rmse:

            transition_to_stage(
                client, model_name, model_staging_version, "Production", True
            )
            latest_stage_version = get_latest_version(client, model_name, "Archived")
            delete_version(client, model_name, latest_stage_version)
    else:
        # If there is not any model in production stage already, transition the staging
        # model to production
        transition_to_stage(
            client, model_name, model_staging_version, "Production", False
        )
