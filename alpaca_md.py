#! python3

import os
import requests
#from alpaca.data.timeframe import TimeFrame
import alpaca
import pandas as pd
from datetime import datetime, timedelta, date
import time
from dotenv import load_dotenv
import json

def show_data(data):
    my_keys = data.keys()
    list_of_my_keys = list(my_keys)
    print ( f"Look at the {list_of_my_keys[0]} data in a Pretty & Nicer format..." )
    print ( f"-----------------------------------------------------------------------" )
    data_list = data[list_of_my_keys[0]]
    for i in range(len(data_list)):
        print ( f"DATA ITEM #{i} is -> {data_list[i]}" )

    return data_list

############################## MAIN #############################################
# this is example code to show how to access and use the Alpaca python module
def main():
    load_status = load_dotenv()
    if load_status is False:
        raise RuntimeError('Environment variables not loaded.')
    else:
	    # Retrieve Alpacc credentials from environment variables
        API_KEY = os.getenv("ALPACA_API-KEY")
        SECRET_KEY = os.getenv("ALPACA_SEC-KEY")

    # Check if keys are available
    if not API_KEY or not SECRET_KEY:
        raise ValueError("Alpaca API credentials not found in environment variables.")

    DATA_BASE_URL = "https://data.alpaca.markets/v2/"
    
    SB_URL = '{}'.format(DATA_BASE_URL)

    SB_URL = '{}stocks/bars?'.format(SB_URL)
    SB_URL = '{}&start=2025-06-26T09:30:00-04:00'.format(SB_URL)
    SB_URL = '{}&end=2025-06-27T09:30:00-04:00'.format(SB_URL)
    SB_URL = '{}&limit=100'.format(SB_URL)
    SB_URL = '{}&adjustment=raw&feed=sip&sort=asc'.format(SB_URL)

    SB_URL = '{}&symbols=IBM'.format(SB_URL)
    SB_URL = '{}&timeframe=1Min'.format(SB_URL)
    
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": SECRET_KEY
    }

    response = requests.get(SB_URL, headers=headers )
    data = json.loads(response.text)
    data = response.json()
    #print(f"{json.dumps(data, indent=2)} ")
    print(f"{data}" )

    ################# Style 2 ############################'

if __name__ == '__main__':
    main()
