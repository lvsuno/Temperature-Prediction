from typing import Tuple

from pandas import Series, DataFrame

from temperature_prediction.utils.data_preparation.feature_selector import (
    select_features,
)

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_exporter
def export(data: Tuple[DataFrame, DataFrame, DataFrame], *args, **kwargs) -> Tuple[
    DataFrame,
    DataFrame,
    DataFrame,
    Series,
    Series,
    Series,
]:
    df, df_train, df_val = data
    target = kwargs.get('target', 'Temp (°C)')

    X = select_features(df)
    y: Series = df[target]

    X_train = select_features(df_train)
    X_val = select_features(df_val)
    y_train = df_train[target]
    y_val = df_val[target]

    if kwargs.get('first_training') == '1':
        folder = kwargs.get('OLD_TRAINING_FOLDER')
    else:
        folder = kwargs.get('NEW_DATA_FOLDER')

    print(folder)
    X_train.to_csv(f'{folder}X_train.csv', index=False, sep=',')
    X_val.to_csv(f'{folder}X_val.csv', index=False, sep=',')
    y_train.to_csv(f'{folder}y_train.csv', index=False)
    y_val.to_csv(f'{folder}y_val.csv', index=False)

    return X, X_train, X_val, y, y_train, y_val


@test
def test_dataset(
    X: DataFrame,
    X_train: DataFrame,
    X_val: DataFrame,
    y: Series,
    y_train: Series,
    y_val: Series,
    *args,
) -> None:
    assert (
        X.shape[1] == 2
    ), f'Entire dataset should have 2 features, but has {X.shape[1]}'
    assert (
        len(y.index) == X.shape[0]
    ), f'Entire dataset should have {X.shape[0]} examples, but has {len(y.index)}'


@test
def test_training_set(
    X: DataFrame,
    X_train: DataFrame,
    X_val: DataFrame,
    y: Series,
    y_train: Series,
    y_val: Series,
    *args,
) -> None:
    assert (
        X_train.shape[1] == 2
    ), f'Training set for training model should have 3 features, but has {X_train.shape[1]}'
    assert (
        len(y_train.index) == X_train.shape[0]
    ), f'Training set for training model should have {X_train.shape[0]} examples, but has {len(y_train.index)}'


@test
def test_validation_set(
    X: DataFrame,
    X_train: DataFrame,
    X_val: DataFrame,
    y: Series,
    y_train: Series,
    y_val: Series,
    *args,
) -> None:
    assert (
        X_val.shape[1] == 2
    ), f'Training set for validation should have 2 features, but has {X_val.shape[1]}'
    assert (
        len(y_val.index) == X_val.shape[0]
    ), f'Training set for training model should have {X_val.shape[0]} examples, but has {len(y_val.index)}'
