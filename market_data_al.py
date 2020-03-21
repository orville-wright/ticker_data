#!/usr/bin/python3

import requests
import alpaca_trade_api as tradeapi
import pandas as pd
import datetime

BASEURL = 'https://paper-api.alpaca.markets'
ACCURL = '{}/v2/account'.format(BASEURL)
POSURL = '{}/v2/positions'.format(BASEURL)

UNKNOWN = 'api.alpaca.markets/paper-api.alpaca.markets'

APIKEY = "PK61TNWINAVOEE9C610J"
SECRETKEY = "oqsxqFZWaIEj7Tu3ev4o8kCcttieV6kuvbV4CAtk"

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
    rx = tradeapi.REST('PK61TNWINAVOEE9C610J', 'oqsxqFZWaIEj7Tu3ev4o8kCcttieV6kuvbV4CAtk', 'https://paper-api.alpaca.markets', 'v2' )
    acct_info = rx.get_account()
    pos_info = rx.list_positions()

    #print ( f"---------------- Account info ------------------" )
    #print ( acct_info )

    #print ( f"---------------- Positions info ------------------" )
    #for i in range(len(pos_info)):
    #    print ( f"Item #{i} \n {pos_info[i]}" )

    print ( " " )
    print ( f"---------------- Stock price info ------------------" )
    print ( " " )
    print ( f"Looking at the RAW format data we extracted..." )
    print ( f"---------------------------------------------------" )

    price_info = rx.get_barset(symbols='CODX', timeframe='1Min', limit=15)
    stock_bars = price_info['CODX']
    print ( f"{price_info}" )
    print ( " " )

    #for k, v in price_info.items():
    #    print ( f"**KEY: {k}" )
    print ( f"Some info about the data..." )
    print ( f"-----------------------------------" )
    my_keys = price_info.keys()
    list_of_my_keys = list(my_keys)
    print ( f"List of all stocks symbols held inside this data DICTionary: {list_of_my_keys}" )
    print ( f"How many stock symbols are inside this data dictionary: {len(list_of_my_keys)}" )
    print ( f"Dictionary KEY # 0 is for symbol: {list_of_my_keys[0]}" )
    print ( " " )
    print ( f"Looking at the raw data iside the {list_of_my_keys[0]} dataset..." )
    print ( f"{stock_bars}" )

    print ( " " )
    print ( f"Now look at the {list_of_my_keys[0]} data in a Pretty & Nicer format..." )
    print ( f"-----------------------------------------------------------------------" )
    data_list = show_data(price_info)

    # Now access very specific parts of the data strcuitures
    num_of_datapoints = len(data_list)
    first_open = stock_bars[0].o
    last_close = stock_bars[-1].c
    percent_change = round( ((last_close - first_open) / first_open * 100),4 )
    print ( " " )
    print ( f"Now ACCESS specific data fields from the complex data structure..." )
    print ( f"---------------------------------------------------------------" )
    print ( f"FIRST OPEN price: {first_open}" )
    print ( f"LAST CLOSE price: {last_close}" )
    print ( "CODX moved {}% in the last {} data points.".format(percent_change, num_of_datapoints))

    print ( " " )
    print ( f"Get and create date & time info..." )
    print ( f"---------------------------------------------------------------" )

    dt_now = datetime.datetime.now()
    dt_now_iso = dt_now.isoformat(timespec='seconds')
    dt_year = datetime.datetime.now().year
    dt_month = datetime.datetime.now().month
    dt_day = datetime.datetime.now().day
    dt_hour = datetime.datetime.now().hour
    dt_min = datetime.datetime.now().minute
    dt_sec = datetime.datetime.now().second
    dt_tz =  datetime.datetime.now().tzinfo

    start_time = datetime.datetime(year=dt_year, month=dt_month, day=dt_day, hour=9, minute=30, second=00).isoformat(timespec='seconds')
    end_time = datetime.datetime(year=dt_year, month=dt_month, day=dt_day, hour=9, minute=32, second=00).isoformat(timespec='seconds')

    print ( "YEAR: {} MONTH: {} DAY: {} HOURS: {} MINUTES: {} SECONDS: {} TZ: {}".format(dt_year, dt_month, dt_day, dt_hour, dt_min, dt_sec, dt_tz) )
    #start_time = datetime.datetime(year=dt_year, month=dt_month, day=dt_day)
    print ( f"** ISO formatted date/time now: {dt_now_iso}" )
    print ( f"** Target START_TIME: {start_time}" )
    print ( f"** Target END: {end_time}" )
    print ( "  " )

    uber_price_info = rx.get_barset(symbols='UBER', timeframe='minute' )
    #uber_price_info = rx.get_barset(symbols='UBER', timeframe='1Min' )
    uber_stock_bars = uber_price_info['UBER']
    print ( f"{uber_price_info}" )
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
