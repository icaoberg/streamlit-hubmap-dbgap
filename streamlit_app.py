import streamlit as st
import pandas as pd
import requests
from pprint import pprint
from datetime import date
from datetime import datetime

# Set the page configuration to wide layout
st.set_page_config(layout="wide")

logo_url = 'https://insidebigdata.com/wp-content/uploads/2020/09/HuBMAP_logo.png'
st.image(logo_url)

title = '''# The Human BioMolecular Atlas Program (HuBMAP)
## Simple observation of dbGaP datasets
'''
st.write(title)

from datetime import date

# Get today's date
today = date.today().strftime("%Y-%m-%d")
st.write(today)

## DO NOT MODIFY THIS BLOCK
# Function to determine the type
def determine_type(dataset_type: str) -> str:
    if '[' in dataset_type and ']' in dataset_type:
        return 'Derived'
    else:
        return 'Primary'
    
def timestamp_to_date(timestamp):
   datetime_obj = datetime.fromtimestamp(timestamp)
   date = datetime_obj.date()
   return date


@st.cache_data
def get_data() -> pd.DataFrame:
    """
    Fetch data from a predefined URL, extract the 'data' key,
    and return it as a DataFrame.

    Returns:
    pd.DataFrame: The data extracted from the 'data' key loaded into a DataFrame.
    """
    url = "https://ingest.api.hubmapconsortium.org/datasets/data-status"  # The URL to get the data from
    try:
        response = requests.get(url)  # Send a request to the URL to get the data
        response.raise_for_status()  # Check if the request was successful (no errors)
        json_data = response.json()  # Convert the response to JSON format

        # Ensure 'data' key exists in the JSON
        if 'data' in json_data:  # Check if the JSON contains the key 'data'
            df = pd.DataFrame(json_data['data'])  # Create a DataFrame using the data under 'data' key
            df = df[df['status']=='Published']
            df = df[df['data_access_level']=='protected']
            df['dataset_status'] = df['dataset_type'].apply(determine_type)
            df['published_timestamp'] = df['published_timestamp']/1000
            df['date'] = df['published_timestamp'].apply(timestamp_to_date)
            columns = ['hubmap_id', 'date', 'uuid', 'group_name']
            df = df[columns]
            if 'hubmap_id' in df.columns:
                # Set the hubmap_id as the new index
                df.set_index('hubmap_id', inplace=True)
        else:
            raise KeyError("'data' key not found in the JSON response")  # Raise an error if 'data' key is missing

        return df  # Return the DataFrame with the data
    except (ValueError, KeyError) as e:  # Catch errors related to value or missing keys
        print(f"Error loading data: {e}")  # Print the error message
        return pd.DataFrame()  # Return an empty DataFrame if there is an error
    except requests.RequestException as e:  # Catch errors related to the request itself
        print(f"Request failed: {e}")  # Print the error message
        return pd.DataFrame()  # Return an empty DataFrame if the request fails

df = get_data()
## DO NOT MODIFY THIS BLOCK

text = '## Published data'
st.write(text)
st.dataframe(df)
