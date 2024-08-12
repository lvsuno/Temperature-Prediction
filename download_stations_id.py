import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Specify Parameters
PROVINCES = [
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NT",
    "NS",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
]  # Province list
MAX_PAGES = [
    4,
    4,
    2,
    1,
    1,
    1,
    1,
    2,
    4,
    1,
    4,
    2,
    1,
]  #  Number of pages knowing that each display 100 rows
NB_STATIONS = [
    319,
    367,
    107,
    40,
    95,
    99,
    67,
    124,
    308,
    17,
    332,
    117,
    48,
]  # number of stations since 2014
START_YEAR = "2014"  # I want the results to go back to at least 2006 or earlier
DATA_FOLDER = 'data/stations/'


def parse_station_id(soup_frames, prov):
    """
    Parse station_id per province and save it.
    Use the downloaded pages in Soup and parse it.
    Parameters
    ------------
        soup_frames: BeautifulSoup List
            The list of downloaded pages
        province: string
            The province abbreviation


    Return
    ------------
     The final table have the following columns:
     [station, name, intervals, min_year, max_year, province]
    """
    #  Empty list to store the station data
    station_data = []

    for soup1 in soup_frames:  # For each soup
        forms = soup1.findAll(
            "form", {"id ": re.compile('stnRequest*')}
        )  #  We find the forms with the stnRequest* ID using regex
        for form in forms:
            try:
                # The stationID is a child of the form
                station = form.find("input", {"name": "StationID"})['value']

                # The station name is a sibling of the input element named lstProvince
                name = (
                    form.find("input", {"name": "lstProvince"})
                    .find_next_siblings("div")[0]
                    .text
                )

                # The intervals are listed as children in a 'select' tag named timeframe
                timeframes = form.find("select", {"name": "timeframe"}).findChildren()
                intervals = [t.text for t in timeframes]

                # We can find the min and max year of this station using the first and last child
                years = form.find("select", {"name": "Year"}).findChildren()
                min_year = years[0].text
                max_year = years[-1].text

                # Store the data in an array
                data = [station, name, intervals, min_year, max_year, prov]
                station_data.append(data)
            except:
                pass

    # Create a pandas dataframe using the collected data and give it the appropriate column names
    stations_df = pd.DataFrame(
        station_data,
        columns=[
            'StationID',
            'Name',
            'Intervals',
            'Year Start',
            'Year End',
            'Province',
        ],
    )
    # stations_df.head()
    stations_df.to_csv(f'{DATA_FOLDER}stations_{prov}.csv')


if __name__ == '__main__':
    """
    Main script to download the pages
    """

    for idx, province in enumerate(PROVINCES):
        # Store each page in a list and parse them later
        soup_frames = []
        for i in range(MAX_PAGES[idx]):
            startRow = 1 + i * 100
            print(f'Downloading Page: {i} for province {province}')

            base_url_1 = "http://climate.weather.gc.ca/historical_data/"
            base_url = f"{base_url_1}search_historic_data_stations_e.html?"
            base_queryProvince = "searchType=stnProv&timeframe=1&lstProvince="
            queryProvince = f"{base_queryProvince}{province}&optLimit=yearRange&"
            base_queryYear = f"StartYear={START_YEAR}&EndYear=2024&Year=2024&Month=7&"
            queryYear = f"{base_queryYear}Day=20&selRowPerPage=100&txtCentralLatMin=0&txtCentralLatSec=0&txtCentralLongMin=0&txtCentralLongSec=0&"
            queryStartRow = f"startRow={startRow}"

            response = requests.get(
                base_url + queryProvince + queryYear + queryStartRow, timeout=300
            )  # Using requests to read the HTML source
            soup = BeautifulSoup(
                response.text, 'html.parser'
            )  # Parse with Beautiful Soup
            soup_frames.append(soup)
        parse_station_id(soup_frames, province)
