from typing import List, Optional

import pandas as pd

CATEGORICAL_FEATURES = ['Station ID']
NUMERICAL_FEATURES = ['Date_Time_Num']


def select_features(
    df: pd.DataFrame, features: Optional[List[str]] = None
) -> pd.DataFrame:
    columns = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
    if features:
        columns += features

    return df[columns]
