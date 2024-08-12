from typing import List, Tuple, Union

from pandas import Index, DataFrame, concat


def dosplit_train(df: DataFrame, feature: str, thres: float):

    min_date = df[feature].min()
    max_date = df[feature].max()

    a = df['Date_Time_Num'] <= (min_date + thres * (max_date - min_date))
    return df[a]


def dosplit_val(df: DataFrame, feature: str, thres: float):

    min_date = df[feature].min()
    max_date = df[feature].max()

    a = df['Date_Time_Num'] > (min_date + thres * (max_date - min_date))
    return df[a]


def split_on_percentage(
    df: DataFrame,
    feature: str,
    percentage: Union[float, int],
    group='Station ID',
    drop_feature: bool = True,
    return_indexes: bool = False,
) -> Union[Tuple[DataFrame, DataFrame], Tuple[Index, Index]]:

    if not group:
        df_train = dosplit_train(df, feature, percentage)
        df_val = dosplit_val(df, feature, percentage)
    else:
        df_train = []
        df_val = []
        for station_id in df['Station ID'].unique():
            df1 = df[df['Station ID'] == station_id]
            df_train.append(dosplit_train(df1, feature, percentage))
            df_val.append(dosplit_val(df1, feature, percentage))
        df_train = concat(df_train)
        df_val = concat(df_val)

    if return_indexes:
        return df_train.index, df_val.index

    if drop_feature:
        df_train = df_train.drop(columns=[feature])
        df_val = df_val.drop(columns=[feature])

    return df_train, df_val
