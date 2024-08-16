import os
from datetime import datetime, timedelta

import pandas as pd
from dateutil import rrule

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from mage_ai.data_preparation.variable_manager import set_global_variable

STATIONS_FOLDER = 'data/stations/'
OLD_TRAINING_FOLDER = 'data/Training/old/'
NEW_DATA_FOLDER = 'data/Training/new/'


# Call Environment Canada API
# Returns a dataframe of data
def getHourlyData(stationID, year, month, day=None):
    base_url = "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?"
    if day:
        query_url = f"format=csv&stationID={stationID}&Year={year}&Month={month}&Day={day}&timeframe=1"
    else:
        query_url = (
            f"format=csv&stationID={stationID}&Year={year}&Month={month}&timeframe=1"
        )
    api_endpoint = base_url + query_url
    return pd.read_csv(api_endpoint, skiprows=0)


@data_loader
def ingest_files(**kwargs) -> pd.DataFrame:
    """
    Template for loading data from API
    """

    now = kwargs.get('execution_date')
    end_date = now - timedelta(days=1)

    stations_df = pd.read_csv(f'{STATIONS_FOLDER}clean_stations_ON_2024.csv')
    All = []
    if not os.path.isfile(f'{OLD_TRAINING_FOLDER}X_train.csv'):
        print("New run. WE've never trained the model before")
        set_global_variable('data_preparation', 'first_training', 1)
        start_date = datetime.strptime('2024 June 01', '%Y %B %d')
        for stationID in stations_df['StationID']:
            frames = []
            for dt in rrule.rrule(
                rrule.MONTHLY, dtstart=start_date, until=end_date.date()
            ):
                df = getHourlyData(stationID, dt.year, dt.month)
                if df['Temp (°C)'].isnull().sum() != df.shape[0]:
                    frames.append(df)

            if frames:

                weather_data = pd.concat(frames)
                ## Use this to remove the uncomplete data for the rest of a month starting from yesterday

                weather_data['Date/Time (LST)'] = pd.to_datetime(
                    weather_data['Date/Time (LST)']
                )
                weather_data['Temp (°C)'] = pd.to_numeric(weather_data['Temp (°C)'])
                weather_data['Station ID'] = stationID
                weather_data['Date (LST)'] = weather_data['Date/Time (LST)'].dt.date
                weather_data = weather_data.loc[
                    weather_data['Date (LST)'] <= end_date.date()
                ]
                # weather_data['Mean Temp (°C)'] = weather_data['Temp (°C)'].groupby(weather_data['Date (LST)']).transform('mean')
                if weather_data['Temp (°C)'].isnull().sum() != 0:
                    # Do a simple linear interpolation
                    # In this project we don't really care about accuracy
                    weather_data['Temp (°C)'] = weather_data['Temp (°C)'].interpolate()
                All.append(weather_data)
        all_weather_data = pd.concat(All)

    else:
        set_global_variable('data_preparation', 'first_training', 0)
        print("It's a new data coming into the system")
        for stationID in stations_df['StationID']:
            weather_data = getHourlyData(
                stationID, end_date.year, end_date.month, end_date.day
            )
            if weather_data['Temp (°C)'].isnull().sum() != weather_data.shape[0]:

                weather_data['Date/Time (LST)'] = pd.to_datetime(
                    weather_data['Date/Time (LST)']
                )
                weather_data['Temp (°C)'] = pd.to_numeric(weather_data['Temp (°C)'])
                weather_data['Station ID'] = stationID
                weather_data['Date (LST)'] = weather_data['Date/Time (LST)'].dt.date
                weather_data = weather_data.loc[
                    weather_data['Date (LST)'] <= end_date.date()
                ]
                # weather_data['Mean Temp (°C)'] = weather_data['Temp (°C)'].groupby(weather_data['Date (LST)']).transform('mean')
                if weather_data['Temp (°C)'].isnull().sum() != 0:
                    # Do a simple linear interpolation
                    # In this project we don't really care about accuracy
                    weather_data['Temp (°C)'] = weather_data['Temp (°C)'].interpolate()

                All.append(weather_data)

        if All:
            all_weather_data = pd.concat(All)
            # all_weather_data = all_weather_data[all_weather_data['Stn Press (kPa)'].notna()]

    return all_weather_data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output.shape[1] == 32, 'The output must have 32 fields'
