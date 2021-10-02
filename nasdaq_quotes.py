#!/usr/bin/python3
import requests
from requests import Request, Session
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
import threading
import json

from bigcharts_md import bc_quote

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class nquote:
    """Class to get live Market Data Quote from NASDAQ.com data source"""

    # global accessors
    quote = {}              # quote as dict
    quote_df0 = ""          # quote as pandas DataFrame
    quote_json0 = ""        # JSON dataset #1 basic info
    quote_json1 = ""        # JSON dataset #1 quote summary
    quote_json2 = ""        # JSON dataset #2 quote watchlist
    quote_json3 = ""        # JSON dataset #3 quote premarket
    data0 = []              # JSON data payload
    yti = 0                 # Unique instance identifier
    cycle = 0               # class thread loop counter
    args = []               # class dict to hold global args being passed in from main() methods
    js_session = ""         # main requests session
    js_resp0 = ''           # session response handle for : self.quote_url
    js_resp1 = ''           # session response handle for : self.summary_url
    js_resp2 = ''           # session response handle for : self.watchlist_url
    js_resp3 = ''           # session response handle for : self.premarket_url
    quote_url = ""
    summary_url = ""
    watchlist_url = ""
    premarket_url = ""
    path = ""


                            # NASDAQ.com header/cookie hack
    nasdaq_headers = { \
                    'authority': 'api.nasdaq.com', \
                    'path': '/api/quote/IBM/info?assetclass=stocks', \
                    'origin': 'https://www.nasdaq.com', \
                    'referer': 'https://www.nasdaq.com', \
                    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"', \
                    'sec-ch-ua-mobile': '"?0"', \
                    'sec-fetch-mode': 'cors', \
                    'sec-fetch-site': 'same-site', \
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' }


    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
        # init empty DataFrame with preset colum names
        self.args = global_args                                # Only set once per INIT. all methods are set globally
        #self.quote_df0 = pd.DataFrame(columns=[ 'Symbol', 'Co_name', 'arrow_updown', 'Cur_price', 'Prc_change', 'Pct_change', 'Open_price', 'Prev_close', 'Vol', 'Mkt_cap', 'Exch_timestamp', 'Time' ] )
        self.yti = yti
        self.js_session = HTMLSession()                        # init JAVAScript processor early
        self.js_session.cookies.update(self.nasdaq_headers)    # load DEFAUKT cookie/header hack package into session
        return

# method 1
    def update_headers(self, symbol):
        cmi_debug = __name__+"::"+self.update_headers.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        self.symbol = symbol.upper()
        logging.info('%s - set cookies/headers path: object' % cmi_debug )
        self.path = '/api/quote/' + self.symbol + '/info?assetclass=stocks'
        #self.nasdaq_headers['path'] = self.path
        self.js_session.cookies.update({'path': self.path} )
        logging.info('nasdaq_quotes::update_headers.## - cookies/headers path: object: %s' % self.path )
        return

# method 2
    def update_cookies(self):
        # assumes that the requests session has already been established
        cmi_debug = __name__+"::"+self.update_cookies.__name__+".#"+str(self.yti)
        logging.info('%s - REDO the cookie extract & update  ' % cmi_debug )
        self.js_session.cookies.update({'ak_bmsc': self.js_resp0.cookies['ak_bmsc']} )    # NASDAQ cookie hack
        return

# method 3
    def form_api_endpoint(self, symbol):
        """
        This is the quote endppints for the req get()
        As of 1 Oct, 2021...Nasdaq has a new data model that splits quote data across 4 key API endpoints. Of which,  2 are very intersting.
        """
        cmi_debug = __name__+"::"+self.form_api_endpoint.__name__+".#"+str(self.yti)
        logging.info('%s - form API endpoint URL' % cmi_debug )
        self.symbol = symbol.upper()
        self.quote_url = "https://api.nasdaq.com" + self.path
        self.summary_url = "https://api.nasdaq.com/api/quote/" + self.symbol + "/summary?assetclass=stocks"
        self.premarket_url = "https://api.nasdaq.com/api/quote/" + self.symbol + "/extended-trading?assetclass=stocks&markettype=pre"
        #
        self.watchlist_url = "https://api.nasdaq.com/api/quote/watchlist?symbol=" + self.symbol + "%7cstocks"
        self.wurl_log1 = "https://api.nasdaq.com/api/quote/watchlist?symbol=" + self.symbol    # hack f-strings doesnt like "%" inside {}
        self.wurl_log2 = "7cstocks"         # hack f-strings doesnt like "%" inside {}
        #
        logging.info( f"================================ Quote API endpoints ================================" )
        logging.info( f"%s - API endpoint #0: [ {self.quote_url} ]" % cmi_debug )
        logging.info( f"%s - API endpoint #1: [ {self.summary_url} ]" % cmi_debug )
        logging.info( f"%s - API endpoint #2: [ {self.wurl_log1}%%{self.wurl_log2} ]" % cmi_debug )
        logging.info( f"%s - API endpoint #3: [ {self.premarket_url} ]" % cmi_debug )
        self.quote_url = self.quote_url
        return

# method 4
    def do_simple_get(self):
        """
        A basic connection/cookie/headers setup method
        INFO: we simply ping www.nasdaq.com. No need for an API specific url. That comes later.
        Assumes the cookies have already been set up
        NO cookie update done!!!
        """
        cmi_debug = __name__+"::"+self.init_blind_session.__name__+".#"+str(self.yti)
        logging.info('%s - Blind request get() on base url' % cmi_debug )
        with self.js_session.get('https://www.nasdaq.com', stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - Request get() done' % cmi_debug )
        # if the get() succeds, the response handle is automatically saved in Class Global accessor -> self.js_resp0
        return

# method 5
    def init_dummy_session(self):
        """
        a cookie setup method
        note: we ping www.nasdaq.com. No need for a API specific url, as this should be the FIRST get
        Our goal is simply find & extract secret cookies. Nothing more.
        """
        cmi_debug = __name__+"::"+self.init_dummy_session.__name__+".#"+str(self.yti)
        with self.js_session.get('https://www.nasdaq.com', stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - extract & update GOOD cookie  ' % cmi_debug )
            self.js_session.cookies.update({'ak_bmsc': self.js_resp0.cookies['ak_bmsc']} )    # NASDAQ cookie hack
        # if the get() succeds, the response handle is automatically saved in Class Global accessor -> self.js_resp0
        return

# method 6
    def get_nquote(self, symbol):
        """
        Access NEW nasdaq.com JAVASCRIPT page [unusual volume] and extract the native JSON dataset
        JSON data contains *BOTH* UP vol & DOWN vol for top 25 symbols, right now!
        NO BeautifulSOup scraping needed anymore. We access the pure JSON datset via native API rest call
        NOTE: Javascript engine process is NOT required as the output page is simple JSON text
        WWARNING: API URL get success for any URL endpoint. This includes non-existent symbols & symbols
                 that return bad/NULL data set (i.e. ETF's, which are not company's or regular symbols)
        NOTE: Since Nasdaq changed the data model, quote data is now split across mutliple API endpoints
        """
        cmi_debug = __name__+"::"+self.get_nquote.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        self.qs = symbol

        with self.js_session.get(self.summary_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp1:
            logging.info( '%s - Stage #1 / Summary / reading data / storing...' % cmi_debug )
            self.quote_json1 = json.loads(self.js_resp1.text)
            logging.info( '%s - Stage #1 - Done' % cmi_debug )

        with self.js_session.get(self.watchlist_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp2:
            logging.info( '%s - Stage #2 / Watchlist / reading data / storing...' % cmi_debug )
            self.quote_json2 = json.loads(self.js_resp2.text)
            logging.info( '%s - Stage #2 - Done' % cmi_debug )

        with self.js_session.get(self.premarket_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp3:
            logging.info( '%s - Stage #3 / premarket / reading data / storing...' % cmi_debug )
            self.quote_json3 = json.loads(self.js_resp3.text)
            logging.info( '%s - Stage #3 - Done' % cmi_debug )

        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"===================== get_nquote.{self.yti} session cookies : {self.qs} ===========================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"===================== get_nquote.{self.yti} session cookies : {self.qs} ===========================" )
        return

# method 7
    def get_js_nquote(self, symbol):
        """
        Access NEW nasdaq.com JAVASCRIPT page [unusual volume] and extract the native JSON dataset
        JSON dataset contains *BOTH* UP vol & DOWN vol for top 25 symbols, right now!
        NO BeautifulSOup scraping needed anymore. We access the pure JSON datset via native API rest call
        NOTE: Javascript engine is required, Cant process/read a JS page via requests(). The get() hangs forever
        NOTE: Javascript currently disbaled, since we access he data directly via API endpoint
        """
        cmi_debug = __name__+"::"+self.get_js_nquote.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        self.symbol = symbol
        with self.js_session.get(self.quote_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp1:
            # read the webpage with our Javascript engine processor
            logging.info('%s - Javascript engine processing...' % cmi_debug )
            self.js_resp1.html.render()    # this isn't needed for this URL becuase is a RAW JSON output page. NOT Javascript
            logging.info('%s - Javascript engine completed!' % cmi_debug )
            logging.info('%s - summary json quote data package extracted / storing...' % cmi_debug )
            self.quote_json1 = json.loads(self.js_resp1.text)

        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"========================== {self.yti} - get_js_nquote::session cookies ================================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================== {self.yti} - get_js_nquote::session cookies ================================" )
        return

# method 8
# New method to build a Pandas DataFrame from JSON data structure
    def build_data(self):
        """
        Build-out the full quote data structure thats tidy & clean.
        All fields sourced from the extracted JSON dataset.
        Wrangle, clean, convert, cast & format data as needed.
        """


        def null_prechecker():
            """
            Helper method to check all the json data fields for NULL values.
            We run this before trying to access list indexes, as that will exert an error.
            And its arduous to wrap all this arround the data acessor method. Better to do it early.
            """
            cmi_debug = __name__+"::"+self.null_prechecker.__name__+".#"+str(self.yti)
            logging.info( f'%s - probing json datasets for NULL zones...' % cmi_debug )
            jd_20 = ("symbol", "companyName", "lastSalePrice", "netChange", "percentageChange", "deltaIndicator", "lastTradeTimestampDateTime", "volume" )
            jd_31 = ("consolidated", "volume", "delta" )
            jd_10 = ("PreviousClose", "MarketCap", "TodayHighLow", "AverageVolume", "OneYrTarget", "Beta", "FiftTwoWeekHighLow" )

            x = "self.quote_json2['data'][0]"
            null_errors = 0
            for i in jd_20:
                try:
                    y = x[i]
                except TypeError:
                    print ( f"probe found NULL json data @: {x}/{i}" )
                    null_errors += 1
                else:
                    pass
            jd20_null_errors = null_errors

            x = "self.quote_json3['data']['infoTable']['rows'][0]"
            null_errors = 0
            for i in jd_31:
                try:
                    y = x[i]
                except TypeError:
                    print ( f"probe found NULL json data @: {x}/{i}" )
                    null_errors += 1
                else:
                    pass
            jd31_null_errors = null_errors

            x = "self.quote_json1['data']['summaryData']"
            null_errors = 0
            for i in jd_10:
                try:
                    y = x[i]
                except TypeError:
                    print ( f"probe found NULL json data @: {x}/{i}" )
                    null_errors += 1
                else:
                    pass
            jd10_null_errors = null_errors


            return jd20_null_errors, jd31_null_errors, jd10_null_errors

        ########################################################################

        cmi_debug = __name__+"::"+self.build_data.__name__+".#"+str(self.yti)
        logging.info('%s - build quote data payload from JSON' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - prepare json data accessors' % cmi_debug )

        # capture bad symbols (e.g. ETF's return NULL json payload. They're not real symbols)
        wrangle_errors = 0
        null_count = 0

        a, b, c = null_prechecker()
        print ( f">>>DEBUG<<< : Null prechecks: j20: {a} / j30: {b}, j10: {c}" )

        # WATCHLIST quote data                                                  # Data wrangeling error counter
        if self.quote_json2['data'] is not None:                                # bad symbol TEST == Null json payload
            logging.info('%s - Stage #1 / Accessing data fields...' % cmi_debug )
            jsondata20 = self.quote_json2['data'][0]                            # HEAD of data payload
            co_sym = jsondata20['symbol']                                       # "IBM"
            co_name = jsondata20['companyName']                                 # "International Business Machines Corporation Common Stock"
            price = jsondata20['lastSalePrice']                                 # "$143.32"
            price_net = jsondata20['netChange']                                 # "+4.39"
            price_pct = jsondata20['percentageChange']                          # "3.16%"
            arrow_updown = jsondata20['deltaIndicator']                         # "up"
            price_timestamp = jsondata20['lastTradeTimestampDateTime']          # "2021-10-01T00:00:00"
            vol_abs = jsondata20['volume']                                      # "6,604,064"
            logging.info( '%s - Stage #1 /[8] fields - Done' % cmi_debug )
        else:
            logging.info('%s - Stage #1 / NULL json payload - NOT regular stock' % cmi_debug )        # bad symbol json payload
            self.quote.clear()
            wrangle_errors += -1

        # PRE-MARKET quoet data - 2 data zones
        if self.quote_json3['data'] is not None:                                # bad symbol TEST == Null json payload
            logging.info('%s - Stage #2 / Accessing data fields...' % cmi_debug )
            jsondata30 = self.quote_json3['data']                               # HEAD of data payload 0
            try:
                jsondata31 = self.quote_json3['data']['infoTable']['rows'][0]       # HEAD of data payload 1
            except TypeError:
                logging.info('%s - WARNING / infoTable payload is NULL' % cmi_debug )        # bad symbol json payload
                open_price = "$0.0 0.0 0.0"
                open_volume = 0                                  # e.g. "71,506"
                open_updown = "N/A"                              # e.g. "up"
                wrangle_errors += -1
            else:
                open_price = jsondata31['consolidated']                             # WARN: multi-field string needs splitting/wrangeling e.g. "$140.8 +1.87 (+1.35%)"
                open_volume = jsondata31['volume']                                  # e.g. "71,506"
                open_updown = jsondata31['delta']                                   # e.g. "up"
                logging.info( '%s - Stage #2 / [3] fields - Done' % cmi_debug )
        else:
            logging.info('%s - Stage #2 / zone [data] NULL json payload - NOT regular stock' % cmi_debug )        # bad symbol json payload
            self.quote.clear()
            wrangle_errors += -1

        # SUMMARY quote data
        if self.quote_json1['data'] is not None:                                # bad symbol TEST == Null json payload
            logging.info('%s - Stage #3 / Accessing data fields...' % cmi_debug )
            jsondata10 = self.quote_json1['data']['summaryData']                # HEAD of data payload
            prev_close = jsondata10['PreviousClose']['value']                   # e,g, "$138.93"
            mkt_cap = jsondata10['MarketCap']['value']                          # e.g. "128,460,592,862"
            today_hilo = jsondata10['TodayHighLow']['value']                    # WARN: multi-field string needs splitting/wrangeling e.g. "$143.97/$140.37"
            avg_vol = jsondata10['AverageVolume']['value']                      # e.g. "4,811,121"
            oneyear_target = jsondata10['OneYrTarget']['value']                 # e.g. "$151.00"
            beta = jsondata10['Beta']['value']                                  # e.g. 1.23
            LII_week_hilo = jsondata10['FiftTwoWeekHighLow']['value']           # WARN: multi-field string needs splitting/wrangeling e.g. "$152.84/$105.92"
            logging.info( '%s - Stage #3 / [7] fields - Done' % cmi_debug )
        else:
            logging.info('%s - Stage #2 / NULL json payload - NOT regular stock' % cmi_debug )        # bad symbol json payload
            self.quote.clear()
            wrangle_errors += -1

        # ######### wrangle, clean, cast & prepare the data ##############################################
        logging.info('%s - Begin data wrangle workload...' % cmi_debug )

        co_sym_lj = co_sym.strip()
        #co_sym_lj = np.array2string(np.char.ljust(co_sym, 6) )          # left justify TXT & convert to raw string

        co_name_lj = (re.sub('[\'\"]', '', co_name) )                    # remove " ' and strip leading/trailing spaces
        co_name_lj = np.array2string(np.char.ljust(co_name_lj, 25) )     # left justify & convert to raw string
        co_name_lj = (re.sub('[\']', '', co_name_lj) )                   # remove " ' and strip leading/trailing spaces

        if price == "N/A":
            price_cl = 0
            logging.info('%s - Price is bad, found N/A data' % cmi_debug )
            wrangle_errors += 1
        else:
            price_cl = (re.sub('[ $,]', '', price))                      # remove $ sign

        if price_net == "N/A":
            price_net_cl = 0
            logging.info('%s - Price NET is bad, found N/A data' % cmi_debug )
            wrangle_errors += 1
        elif price_net == 'UNCH':
            price_net_cl = "Unch"
            logging.info('%s - Price NET is unchanged' % cmi_debug )
            wrangle_errors += 1
        else:
            price_net_cl = (re.sub('[\-+]', '', price_net))              # remove - + signs
            price_net_cl = np.float(price_net)

        if price_pct == "N/A":
            price_pct_cl = 0
            logging.info('%s - Price pct is bad, found N/A data' % cmi_debug )
            wrangle_errors += 1
        elif price_pct == "UNCH":
            price_pct_cl = "Unch"
            logging.info('%s - Price pct is unchanged' % cmi_debug )
            wrangle_errors += 1
        elif price_pct == '':
            price_pct_cl = "No data"
            logging.info('%s - Price pct is bad, field is Null/empty' % cmi_debug )
            wrangle_errors += 1
        else:
            price_pct = (re.sub('[\-+%]', '', price_pct))                # remove - + % signs
            price_pct_cl = np.float(price_pct)

        # ################# open price(s) need extra treatment & care...
        if open_price == "N/A" or open_price is None:
            open_price_cl = np.float(0)
            open_price_net = float(0)
            open_price_pct_cl = float(0)
            logging.info( f'%s - WARNING / open_price is bad, found N/A or NULL data: {open_price}' % cmi_debug )
            wrangle_errors += 1
        else:
            ops = open_price.split()
            # data is good...proceed to access 3 indices of sub-data from split list[]

            try:
                open_price = ops[0]                     # e.g. 140.8
            except IndexError:
                logging.info('%s - WARNING / open_price is NULL / setting to: $0.0' % cmi_debug )
                open_price = float(0)
                wrangle_errors += 1
            else:
                open_price_cl = (re.sub('[ $,]', '', open_price))   # remove " " $ ,
                # data is good...

            try:
                open_price_net = ops[1]                 # (test for missing data) - good data =  +1.87
            except IndexError:
                logging.info('%s - WARNING / open_price_net is NULL / setting to: $0.0' % cmi_debug )
                open_price_net = float(0)               # set NULL data to ZERO
                wrangle_errors += 1
                # data is good...

            try:
                open_price_pct = ops[2]                 # (test for missing data) - good data = e.g. (+1.35%)"
            except IndexError:
                logging.info('%s - WARNING / open_price_pct is NULL / setting to: %0.0' % cmi_debug )
                open_price_pct = float(0)               # set NULL data to ZERO
                wrangle_errors += 1
            else:
                open_price_pct_cl = (re.sub('[)(%]', '', price_pct))
            #################################################

        if prev_close == "N/A":
            prev_close_cl = 0
            logging.info('%s - Prev close is bad, found N/A data' % cmi_debug )
            wrangle_errors += 1
        else:
            prev_close_cl = (re.sub('[ $,]', '', prev_close))   # remove $ sign

        if mkt_cap == "N/A":
            mkt_cap_cl = float(0)
            logging.info('%s - Mkt cap is bad, found N/A data' % cmi_debug )
            wrangle_errors += 1
        elif mkt_cap == 0:
            mkt_cap_cl = float(0)
            logging.info('%s - Mkt cap is ZERO, found N/A data' % cmi_debug )
            wrangle_errors += 1
        else:
            mkt_cap_cl = np.float(re.sub('[,]', '', mkt_cap))   # remove ,
            mkt_cap_cl = round(mkt_cap_cl / 1000000, 3)                  # resize & round mantissa = 3, as nasdaq.com gives full num

        vol_abs_cl = (re.sub('[,]', '', vol_abs))                        # remove ,

        # craft final data structure.
        # NOTE: globally accessible and used by quote DF and quote DICT
        self.data0 = [[ \
           co_sym_lj, \
           co_name_lj, \
           arrow_updown, \
           np.float(price_cl), \
           price_net_cl, \
           price_pct_cl, \
           np.float(open_price_cl), \
           np.float(prev_close_cl), \
           np.float(vol_abs_cl), \
           mkt_cap_cl, \
           price_timestamp, \
           time_now ]]

        # craft the quote DICT. Doesn't hurt to do this here as it assumed that the data
        # is all nice & clean & in its final beautiful shape by now.
        logging.info('%s - Build global quote dict' % cmi_debug )        # so we can access it natively if needed, without using pandas
        self.quote = dict( \
                symbol=co_sym_lj.rstrip(), \
                name=co_name, \
                updown=arrow_updown, \
                cur_price=price_cl, \
                prc_change=price_net_cl, \
                pct_change=price_pct_cl, \
                open_price=open_price_cl, \
                prev_close=prev_close_cl, \
                vol=vol_abs_cl, \
                mkt_cap=mkt_cap_cl )

        return wrangle_errors

# method 9
# New method to build a Pandas DataFrame from JSON data structure
    def build_df(self):
        """
        A 1-off nasdaq.com stored in a DataFrame
        Might be useeful oneday?
        """

        cmi_debug = __name__+"::"+self.build_df.__name__+".#"+str(self.yti)
        logging.info('%s - Create quote DF from JSON' % cmi_debug )

        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop ephemeral DF' % cmi_debug )
        #self.quote_df0.drop(self.quote_df0.index, inplace=True)        # ensure the DF is empty

        logging.info('%s - Populate DF with new quote data' % cmi_debug )
        self.quote_df0 = pd.DataFrame(self.data0, columns=[ 'Symbol', 'Co_name', 'arrow_updown', 'Cur_price', 'Prc_change', 'Pct_change', 'Open_price', 'Prev_close', 'Vol', 'Mkt_cap', 'Exch_timestamp', 'Time' ] )
        logging.info('%s - Quote DF created' % cmi_debug )

        return
