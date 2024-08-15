from typing import Dict, Tuple, Union
from pandas import Series
from temperature_prediction.utils.logging import (
    get_best_params,
    register_model,
    track_experiment,
    transition_to_stage,
    update_model_version,
    update_registered_model,
    wait_until_ready,
    delete_version,
    load_models,
)
from scipy.sparse._csr import csr_matrix
# from deepdiff import DeepDiff
from xgboost import Booster
from temperature_prediction.utils.models.xgboost import build_data, train_model

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

from mage_ai.data_preparation.variable_manager import set_global_variable

import os

@data_exporter
def train_and_register(
    settings: Tuple[
        Dict[str, Union[bool, float, int, str]],
        Union[Series, csr_matrix],
    ],
    **kwargs,
) -> Tuple[Booster, float, Series]:
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    # Specify your data exporting logic here
    _, X_train, X_val, y_train, y_val = settings

    training = build_data(X_train, y_train)
    validation = build_data(X_val, y_val)
    # fetch the best parameters that can exist in mlflow for this experiment
    best_params_new = get_best_params()

    # diff = DeepDiff(best_params_new, hyperparameters, significant_digits=1)

   # if ("type_changes"  in diff) or ("values_changed" in diff):
    if 'max_depth' in best_params_new:
        best_params_new['max_depth'] = int(best_params_new['max_depth'])
    
    num_boost_round = int(best_params_new.pop('num_boost_round'))
    model, metrics, y_pred = train_model(training,
                                    validation,
                                    early_stopping_rounds=100,
                                    hyperparameters=best_params_new,
                                    num_boost_round=num_boost_round,
                                    )
    
    
    params_new = best_params_new
    params_new['num_boost_round'] = num_boost_round
    runs = track_experiment(block_uuid='register_best_model',
                    hyperparameters=params_new,
                    metrics= metrics,
                    model= model,
                    pipeline_uuid='training',
                    predictions=y_pred,
                    )
    if not os.getenv('MODEL_NAME') and not kwargs.get('MODEL_NAME'):
        model_name = "temp-pred"
        set_global_variable('training', 'model_name', model_name)
    else:
        model_name = os.getenv('MODEL_NAME')  or kwargs.get('MODEL_NAME')  

    # now = kwargs.get('execution_date')
    # date_time = now.strftime("%Y-%m-%d / %H-%M-%S")

    # model_name = f"{model_name}-{date_time}"
    model_details = register_model(runs.info.run_id,model_name=model_name)
    client = wait_until_ready(model_details.name, model_details.version)

    # Add a high-level description to the registered model, including the machine
    # learning problem and dataset
    description = """
        This model predicts the temperature of a weather station in Ontario (canada).
        We only used two features in this model:
            1. Station ID: Id of the station
            2. Date/Time (LST) (the date and time for which the prediction will be made),
        """        
    update_registered_model(client, model_details.name, description)
    
    version_description= """
    This model version was built using XGBoost Regression. 
    It is the best we have right now. Please Enjoy!
    """
    update_model_version(client, model_details.name, model_details.version, version_description)
    # Transition the model to Staging
    transition_to_stage(client, model_details.name, model_details.version, "staging", False)
    set_global_variable('training', 'staging_model_version', model_details.version)
    
    return model, metrics['rmse'], y_pred