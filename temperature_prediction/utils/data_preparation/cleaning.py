import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """clean the data"""
    # In case there are still unknown Mean temperature
    if df['Temp (°C)'].isnull().sum() != 0:
        # Do a simple linear interpolation
        # In this project we don't really care about accuracy
        df['Temp (°C)'] = df['Temp (°C)'].interpolate()

    # Calculate the trip duration in minutes
    df['Date_Time_Num'] = df['Date/Time (LST)'].apply(lambda td: td.timestamp())

    return df
