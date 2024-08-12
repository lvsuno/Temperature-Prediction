if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

import os
import mlflow
from temperature_prediction.utils.logging import setup_experiment, delete_version
import logging
import pickle

@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # mlflow.set_tracking_uri(os.getenv('DEFAULT_TRACKING_URI'))
    # client, id =setup_experiment()

    # delete_version(client, 'temp-pred', 1)

    
    # print(id)
    #mlflow.delete_experiment(id)
    
    
    
    # logging.getLogger("mlflow").setLevel(logging.DEBUG)

    return pickle.format_version


