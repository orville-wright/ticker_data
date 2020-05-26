#!/usr/bin/python3

import requests
import alpaca_trade_api as tradeapi
import pandas as pd
import datetime
import time
from environs import Env

BASEURL = 'https://paper-api.alpaca.markets'
ACCURL = '{}/v2/account'.format(BASEURL)
POSURL = '{}/v2/positions'.format(BASEURL)

UNKNOWN = 'api.alpaca.markets/paper-api.alpaca.markets'

APIKEY = "_your_key_here_"
SECRETKEY = "_your_key_here_"

################# Style 1 ############################'

#print ( "----------------- Using nice .REST Helper Entity class methods ------------------ ")
#print ( f"**debug** - Base URL: {BASEURL}")
#print ( f"**debug** - Account URL: {ACCURL}")
#print ( f"**debug** - Positions URL: {POSURL}")

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

def main():

    env = Env()
    env.read_env()  # read .env file, will recurrsively hunt for .env file if not in CWD
    # casting api variables
    APIKEY = env.str("ALPACA_API-KEY")
    SECRETKEY = env.str("ALPACA_SEC-KEY")

    print ( " ")
    print ( f"Using API key: {APIKEY}" )
    print ( f"Using SECKEY key: {SECRETKEY}" )
    print ( " ")

    rx = tradeapi.REST(APIKEY, SECRETKEY, 'https://paper-api.alpaca.markets', 'v2' )
    acct_info = rx.get_account()
    pos_info = rx.list_positions()

    price_info = rx.get_barset(symbols='CODX', timeframe='1Min', limit=15)
    stock_bars = price_info['CODX']
    print ( f"{price_info}" )
    print ( " " )

    print ( f"Some info about the data..." )
    print ( f"-----------------------------------" )
    my_keys = price_info.keys()
    list_of_my_keys = list(my_keys)
    print ( f"KEYS: {my_keys}" )
    print ( f"TYpe KEYS: {type(my_keys)}" )
    print ( f"LIST of KEYS 1: {list(my_keys)}" )
    print ( f"LEN of list of keys: {len(list_of_my_keys)}" )
    print ( f"KEY # 0 / 1: {list_of_my_keys[0]}" )
    print ( f"KEY # 0 / 2: {list(my_keys)[0]}" )
    print ( f"ITER price_info: {iter(price_info)}" )
    for i in iter(price_info):
        print ( f"ITERATE over keys: {i}" )
        print ( f"---------------- ITERATE ----------------" )

    print ( f"price_info.values(): {price_info.values()}" )
    print ( " " )
    print ( f"RAW dict data:  {list_of_my_keys[0]} dataset..." )        # same as price_info.values()
    print ( f"{stock_bars}" )

    print ( " " )
    print ( f"Now look at the {list_of_my_keys[0]} data in a Pretty & Nicer format..." )
    print ( f"-----------------------------------------------------------------------" )
    data_list = show_data(price_info)

    # Now access very specific parts of the data strcuitures
    num_of_datapoints = len(data_list)
    first_open = stock_bars[0].o
    last_close = stock_bars[-1].c
    first_time = stock_bars[0].t
    last_time = stock_bars[-1].t
    percent_change = round( ((last_close - first_open) / first_open * 100),4 )
    #f_realtime = time.localtime(first_time)
    #l_realtime = time.localtime(last_time)

    print ( " " )
    print ( f"Now ACCESS specific data fields from the complex data structure..." )
    print ( f"---------------------------------------------------------------" )
    print ( f"FIRST OPEN price: {first_open}" )
    print ( f"LAST CLOSE price: {last_close}" )
    print ( f"FIRST TIME: {type(first_time)} / {first_time}" )
    print ( f"LAST TIME: {type(last_time)} / {last_time}" )

    print ( "CODX moved {}% in the last {} data points.".format(percent_change, num_of_datapoints))

    print ( " " )
    print ( f"Get and create date & time info..." )
    print ( f"---------------------------------------------------------------" )


    dt_now = datetime.datetime.now()
    dt_now_iso = dt_now.isoformat()
    dt_year = datetime.datetime.now().year
    dt_month = datetime.datetime.now().month
    dt_day = datetime.datetime.now().day
    dt_hour = datetime.datetime.now().hour
    dt_min = datetime.datetime.now().minute
    dt_sec = datetime.datetime.now().second
    dt_tz =  datetime.datetime.now().tzinfo

    start_time = datetime.datetime(year=dt_year, month=dt_month, day=dt_day, hour=9, minute=30, second=00).isoformat(timespec='seconds')
    end_time = datetime.datetime(year=dt_year, month=dt_month, day=dt_day, hour=9, minute=32, second=00).isoformat(timespec='seconds')
    p_start_time = pd.Timestamp(year=dt_year, month=dt_month, day=dt_day, hour=9, minute=40, second=00).isoformat()


    print ( "YEAR: {} MONTH: {} DAY: {} HOURS: {} MINUTES: {} SECONDS: {} TZ: {}".format(dt_year, dt_month, dt_day, dt_hour, dt_min, dt_sec, dt_tz) )
    #start_time = datetime.datetime(year=dt_year, month=dt_month, day=dt_day)
    print ( f"** ISO formatted date/time now: {dt_now_iso}" )
    print ( f"** Target START_TIME: {start_time+'-05:00'}" )
    print ( f"** Target END: {end_time+'-05:00'}" )
    print ( f"** pd.START TIME: {p_start_time}" )
    print ( "  " )

    uber_price_info = rx.get_barset(symbols='UBER', timeframe='1Min', start='2020-03-19T09:30:00-04:00', end='2020-03-19T09:35:00-04:00', limit=10 )
    uber_stock_bars = uber_price_info['UBER']
    uber_first_time = uber_stock_bars[0].t
    uber_last_time = uber_stock_bars[-1].t
    this_sym = uber_price_info.keys()
    symb = list(this_sym)

    print ( )
    print ( "{} - START TIME: {}".format(symb[0], uber_first_time) )
    print ( "{} - END TIME: {}".format(symb[0], uber_last_time) )
    #print ( f"{uber_price_info}" )
    print ( " " )
    #ts = pd.Timestamp(year = 2009, month = 5, day = 31, hour = 4, second = 49)
    #print ( f"*** Timestamp test: {ts}" )
    #print ( f"*** ISO Timestamp:  {ts.isoformat()}" )

    show_data(uber_price_info)

    ################# Style 2 ############################'

    # print ( " " )
    # print ( "------------- Testing RAW Request method ---------------" )
    # r = requests.get( ACCURL, headers={'APCA-API-KEY-ID': APIKEY, 'APCA-API-SECRET-KEY': SECRETKEY} )

    #print (r.content)

if __name__ == '__main__':
    main()
