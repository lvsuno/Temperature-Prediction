from typing import Dict, List, Tuple, Callable

from xgboost import Booster
from hyperopt import hp
from hyperopt.pyll import scope


def build_hyperparameters_space(
    model_class: Callable[
        ...,
        Booster,
    ],
    random_state: int = 42,
    **kwargs,
) -> Tuple[Dict, Dict[str, List]]:
    params = {}
    choices = {}

    if Booster is model_class:
        params = {
            # Controls the fraction of features (columns) that will be randomly sampled for each tree.
            "colsample_bytree": hp.uniform('colsample_bytree', 0.5, 1.0),
            # Minimum loss reduction required to make a further partition on a leaf node of the tree.
            "gamma": hp.uniform('gamma', 0.1, 1.0),
            "learning_rate": hp.loguniform('learning_rate', -3, 0),
            # Maximum depth of a tree.
            "max_depth": scope.int(hp.quniform('max_depth', 4, 100, 1)),
            "min_child_weight": hp.loguniform('min_child_weight', -1, 3),
            # Number of gradient boosted trees. Equivalent to number of boosting rounds.
            # n_estimators=hp.choice('n_estimators', range(100, 1000))
            "num_boost_round": hp.quniform('num_boost_round', 500, 1000, 10),
            "objective": 'reg:squarederror',
            # Preferred over seed.
            "random_state": random_state,
            # L1 regularization term on weights (xgb’s alpha).
            "reg_alpha": hp.loguniform('reg_alpha', -5, -1),
            # L2 regularization term on weights (xgb’s lambda).
            "reg_lambda": hp.loguniform('reg_lambda', -6, -1),
            # Fraction of samples to be used for each tree.
            "subsample": hp.uniform('subsample', 0.1, 1.0),
        }

    for key, value in choices.items():
        params[key] = hp.choice(key, value)

    if kwargs:
        for key, value in kwargs.items():
            if value is not None:
                kwargs[key] = value

    return params, choices
