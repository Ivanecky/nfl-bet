# Import libraries
import pandas as pd
import requests as r
from io import StringIO
import os
import polars as pl
import yaml

# Define the base URL, defined to use the NFL data API
base_url = "https://api.the-odds-api.com/v4/historical/sports/americanfootball_nfl/"

# Function to define dates
# Takes in a date in yyyy-MM-dd format and converts it to the proper API format (iso)
def convert_date(dt: str) -> str:
    return(dt + 'T23:59:59Z')


# Function to get the list of events
def get_historical_events(api_key: str, date: str) -> list:
    # Convert the date to fit api call
    api_dt = convert_date(date)
    # Define the base URL
    base_url = "https://api.the-odds-api.com/v4/historical/sports/americanfootball_nfl"
    # Format API call
    api_call = f"{base_url}/events?apiKey={api_key}&date={api_dt}"
    # Make API call
    event_rqst = r.get(api_call)
    # Check if the request was successful
    if event_rqst.status_code != 200:
        raise Exception(f"API request failed with status code {event_rqst.status_code}")
    # Parse out the IDs from the response
    data = event_rqst.json()['data']
    event_ids = [event['id'] for event in data]
    return event_ids

# Function to extract markets
def extract_markets(market_list: list) -> list:
    # Get each available market for an event and return as a list
    avail_mrkts = []
    for i in market_list:
        avail_mrkts.append(i['key']) # extracts the key component
    return(avail_mrkts)

# Function to get the odds from an event ID
def get_event_markets(api_key:str, event_id: str) -> pl.DataFrame:
    # Define base url
    base_url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl"
    # Define the base URL
    mrkt_url =  base_url + f'/events/{event_id}/markets?apiKey={api_key}&regions=us'
    # Make API call
    mrkt_rqst = r.get(mrkt_url)
    # Check if the request was successful
    if mrkt_rqst.status_code != 200:
        raise Exception(f"API request failed with status code {mrkt_rqst.status_code}")
    # Extract the data from the API call
    data = mrkt_rqst.json()
    # Get bookmakers
    bk_df = pl.DataFrame(data['bookmakers'])
    # Explode out markets column
    bk_df = (
        bk_df.with_columns(
            pl.col('markets').map_elements(extract_markets, return_dtype=pl.List(pl.Utf8)).alias('market_list')
        ).drop('markets')
        .rename({
         "key": "book_key"
         , "title": "book_name"   
        })
    )
    # bk_df['market_list'] = bk_df.apply(lambda row: extract_markets(row['markets']), axis=1)
    # Return dataframe
    return(bk_df)

# Main file
if __name__ == "__main__":
    # Read in API key for Odds API access
    with open(os.getcwd() + '/creds/creds.yaml', 'r') as file:
        creds = yaml.safe_load(file)

    # Define API key
    api_key = creds['paid_api_key']

    # code test
    test_history = get_historical_events(api_key=api_key, date='2025-10-31')

    # get the markets for an event
    test_markets = get_event_markets(api_key, test_history[0])
    
