import io
import pandas as pd
from typing import List, Tuple
import pickle

from pandas import DataFrame, Series
from scipy.sparse._csr import csr_matrix
from sklearn.base import BaseEstimator

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from temperature_prediction.utils.data_preparation.feature_selector import select_features
from temperature_prediction.utils.data_preparation.encoders import vectorize_features

@data_loader
def load_data_from_api(*args, **kwargs) -> Tuple[
    csr_matrix,
    csr_matrix,
    Series,
    Series,
]:
    """
    Template for loading data from API
    """
    folder = 'data/Training/'
    df_train = pd.read_csv(f'{folder}old/X_train.csv')
    df_val = pd.read_csv(f'{folder}old/X_val.csv')
    y_train: Series = pd.read_csv(f'{folder}old/y_train.csv')
    y_val: Series = pd.read_csv(f'{folder}old/y_val.csv')

    # Convert location IDs to string to treat them as categorical features
    categorical = ['Station ID']
    df_train[categorical] = df_train[categorical].astype(str)
    df_val[categorical] = df_val[categorical].astype(str)
   
    X_train, X_val, dv = vectorize_features(df_train,df_val)
    
    with open(f'{folder}DictVect/dictvectorizer.bin', 'wb') as f_out:
        pickle.dump(dv, f_out)

    return X_train, X_val, y_train, y_val


@test
def test_set_dimension(  
    X_train: csr_matrix,
    X_val: csr_matrix,
    y_train: Series,
    y_val: Series,
    *args,
) -> None:

    assert (
        X_train.shape[1] == X_val.shape[1]
    ), f'Training set and the validation set for training model should have the same number of features.'
 
@test
def test_training_set(
    X_train: csr_matrix,
    X_val: csr_matrix,
    y_train: Series,
    y_val: Series,
    *args,
) -> None:

    assert (
        len(y_train.index) == X_train.shape[0]
    ), f'Training set for training model should have {X_train.shape[0]} examples, but has {len(y_train.index)}'


@test
def test_validation_set(
    X_train: csr_matrix,
    X_val: csr_matrix,
    y_train: Series,
    y_val: Series,
    *args,
) -> None:
    assert (
        len(y_val.index) == X_val.shape[0]
    ), f'Training set for training model should have {X_val.shape[0]} examples, but has {len(y_val.index)}'
