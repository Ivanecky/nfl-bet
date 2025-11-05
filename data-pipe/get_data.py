# Import libraries
import requests as r
import polars as pl

# Define the base URL, defined to use the NFL data API
base_url = "https://api.the-odds-api.com/"

# Function to define dates
# Takes in a date in yyyy-MM-dd format and converts it to the proper API format (iso)
def convert_date(dt: str) -> str:
    return(dt + 'T23:59:59Z')

# Function to get the list of events
def get_historical_events(api_key: str, date: str) -> list:
    # Convert the date to fit api call
    api_dt = convert_date(date)
    # Define the base URL
    url = base_url + "v4/historical/sports/americanfootball_nfl"
    # Format API call
    api_call = f"{url}/events?apiKey={api_key}&date={api_dt}"
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
    url = base_url + "v4/sports/americanfootball_nfl"
    # Define the base URL
    mrkt_url =  url + f'/events/{event_id}/markets?apiKey={api_key}&regions=us'
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

# Function to get historical odds
def get_historical_odds(api_key: str, markets: list, dt: str) -> pl.DataFrame:
    # format markets arg for api call
    markets_fmt = ",".join(markets)
    # convert the date
    conv_dt = convert_date(dt)
    # format api call
    url = base_url + f'v4/historical/sports/americanfootball_nfl/odds?apiKey={api_key}&regions=us&markets={markets_fmt}&date={conv_dt}'
    # make the API call
    odds_rqst = r.get(url)
    # check if request was valid
    if odds_rqst.status_code != 200:
        raise Exception(f"API request failed with status code {odds_rqst.status_code}")
    # Extract the data from the API call
    data = odds_rqst.json()
    # Convert to polars
    df = pl.DataFrame(data['data'])
    # Subset columns
    df = df.drop('sport_key', 'sport_title')
    # Return data
    return(df)

# Function to get current available events
def get_current_events(api_key: str) -> pl.List:
    # Format URL
    url = base_url + f"/v4/sports/americanfootball_nfl/events?apiKey={api_key}"
    # Make API call
    events_rqst = r.get(url)
    # Check response
    if events_rqst.status_code != 200:
        # Raise exception
        raise Exception(f"API request failed with status code {events_rqst.status_code}")
    # Extract data
    events_df = pl.DataFrame(events_rqst.json())
    # Remove unnecessary columns
    events_df = events_df.drop('sport_key', 'sport_title')
    # Return data
    return(events_df)

# Function to get the current odds available
def get_current_odds(api_key: str, markets: list, event_id: str) -> pl.DataFrame:
    # format markets arg for api call
    markets_fmt = ",".join(markets)
    # create url for api call
    url = base_url + f"/v4/sports/americanfootball_nfl/events/{event_id}/odds?apiKey={api_key}&regions=us&markets={markets_fmt}"
     # make the API call
    odds_rqst = r.get(url)
    # check if request was valid
    if odds_rqst.status_code != 200:
        raise Exception(f"API request failed with status code {odds_rqst.status_code}")
    # Extract the data from the API call
    df = pl.DataFrame(odds_rqst.json())
    # Remove excess columns
    df = df.drop('sport_key', 'sport_title')
    # Return data
    return(df)
