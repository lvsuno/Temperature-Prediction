from typing import Dict, Tuple, Union

import numpy as np
import xgboost as xgb
from pandas import Series
from scipy.sparse._csr import csr_matrix
from xgboost import DMatrix
from temperature_prediction.utils.logging import track_experiment
from temperature_prediction.utils.models.xgboost import build_data, tune_hyperparameters

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def hyperparameter_tuning(
    training_set: Union[Series, csr_matrix],
    **kwargs,
) -> Tuple[
    Dict[str, Union[bool, float, int, str]],
    Tuple[
    csr_matrix,
    csr_matrix,
    Series,
    Series,
],
]:
    X_train, X_val, y_train, y_val= training_set

    training = build_data(X_train, y_train)
    validation = build_data(X_val, y_val)

    best_hyperparameters = tune_hyperparameters(
        training,
        validation,
        callback=lambda **opts: track_experiment(**{**opts, **kwargs}),
        **kwargs,
    )

    return best_hyperparameters , X_train, X_val, y_train, y_val
