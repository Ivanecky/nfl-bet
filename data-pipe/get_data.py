# Import libraries
import pandas as pd
import requests as r
from io import StringIO
import os
import polars as pl
import yaml

# Define the base URL, defined to use the NFL data API
base_url = "https://api.the-odds-api.com/v4/historical/sports/americanfootball_nfl/"

# Read in API key for Odds API access
with open(os.getcwd() + '/creds/creds.yaml', 'r') as file:
    creds = yaml.safe_load(file)

# Define API key
api_key = creds['paid_api_key']

# Function to define dates
# Takes in a date in yyyy-MM-dd format and converts it to the proper API format (iso)
def convert_date(dt: str):
    return(dt + 'T23:59:59Z')


# Function to get the list of events
def get_historical_events(api_key: str, date: str):
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
def extract_markets(df: pd.DataFrame):
    # Get each available market for an event and return as a list
    markets = df['markets']
    avail_mrkts = list()
    for i in markets:
        for k in i:
            avail_mrkts = avail_mrkts.append(k['key'])

# Function to get the odds from an event ID
def get_event_markets(api_key:str, event_id: str):
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
    bk_df = pd.DataFrame(data['bookmakers'])
    # Explode out markets column
    bk_df['']


if __name__ == "__main__":
    # code test
    test_history = get_historical_events(api_key=api_key, date='2025-10-31')

    # extract information from each event

