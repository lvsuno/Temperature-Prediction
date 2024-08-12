from typing import Tuple

import pandas as pd

from temperature_prediction.utils.data_preparation.cleaning import clean
from temperature_prediction.utils.data_preparation.splitters import split_on_percentage
from temperature_prediction.utils.data_preparation.feature_selector import (
    select_features,
)

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer


@transformer
def transform(
    df: pd.DataFrame, **kwargs
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    split_on_feature = kwargs.get('split_on_feature')
    split_on_feature_percentage = kwargs.get('split_on_feature_percentage')
    target = kwargs.get('target')

    df = clean(df)
    df = select_features(df, features=[target])

    df_train, df_val = split_on_percentage(
        df,
        split_on_feature,
        split_on_feature_percentage,
        drop_feature=False,
    )

    return df, df_train, df_val
