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
    quote_json0 = ""        # JSON dataset #1 : dummy_session + Update_cookiues + do_simple_get
    quote_json1 = ""        # JSON dataset #1 quote summary
    quote_json2 = ""        # JSON dataset #2 quote watchlist
    quote_json3 = ""        # JSON dataset #3 quote premarket
    quote_json4 = ""        # JSON dataset #4 quote asset_class
    data0 = []              # JSON data payload
    yti = 0                 # Unique instance identifier
    cycle = 0               # class thread loop counter
    args = []               # class dict to hold global args being passed in from main() methods
    js_session = ""         # main requests session
    js_resp0 = ''           # session response handle for : dummy_session + Update_cookiues + do_simple_get
    js_resp1 = ''           # session response handle for : self.summary_url
    js_resp2 = ''           # session response handle for : self.watchlist_url
    js_resp3 = ''           # session response handle for : self.premarket_url
    js_resp4 = ''           # session response handle for : self.info_url
    quote_url = ""
    summary_url = ""
    watchlist_url = ""
    premarket_url = ""
    info_url = ""
    path = ""
    asset_class = ""        # global NULL TESTing indicator (important)


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
    def update_headers(self, symbol, asset_class):
        cmi_debug = __name__+"::"+self.update_headers.__name__+".#"+str(self.yti)
        logging.info( f"%s - CALLED" % cmi_debug )
        self.symbol = symbol.upper()
        path = "/api/quote/" + self.symbol + "/info?assetclass=" + asset_class
        self.js_session.cookies.update({'path': path} )
        logging.info( f"%s - cookies/headers [path] object set to: {path}" % cmi_debug )
        return

# method 2
    def update_cookies(self):
        # assumes that the requests session has already been established
        cmi_debug = __name__+"::"+self.update_cookies.__name__+".#"+str(self.yti)
        logging.info('%s - REDO the cookie extract & update  ' % cmi_debug )
        self.js_session.cookies.update({'ak_bmsc': self.js_resp0.cookies['ak_bmsc']} )    # NASDAQ cookie hack
        return

# method 3
    def form_api_endpoint(self, symbol, asset_class):
        """
        This is the quote endppints for the req get()
        As of 1 Oct, 2021...Nasdaq has a new data model that splits quote data across 4 key API endpoints. Of which,  2 are very intersting.
        """
        cmi_debug = __name__+"::"+self.form_api_endpoint.__name__+".#"+str(self.yti)
        logging.info('%s - form API endpoint URL' % cmi_debug )
        self.symbol = symbol.upper()
        self.quote_url = "https://api.nasdaq.com/api/quote/" + self.symbol + "/info?assetclass=" + asset_class
        self.info_url = "https://api.nasdaq.com/api/quote/" + self.symbol + "/info?assetclass=" + asset_class
        self.summary_url = "https://api.nasdaq.com/api/quote/" + self.symbol + "/summary?assetclass=" + asset_class
        self.premarket_url = "https://api.nasdaq.com/api/quote/" + self.symbol + "/extended-trading?assetclass=" + asset_class + "&markettype=pre"
        #
        self.watchlist_url = "https://api.nasdaq.com/api/quote/watchlist?symbol=" + self.symbol + "%7c" + asset_class
        wurl_log1 = "https://api.nasdaq.com/api/quote/watchlist?symbol=" + self.symbol    # hack f-strings doesnt like "%" inside {}
        wurl_log2 = f"7c{asset_class}"         # hack f-strings doesnt like "%" inside {}
        #
        logging.info( f"================================ Quote API endpoints ================================" )
        logging.info( f"%s - API endpoint #0: [ {self.quote_url} ]" % cmi_debug )
        logging.info( f"%s - API endpoint #1: [ {self.summary_url} ]" % cmi_debug )
        logging.info( f"%s - API endpoint #2: [ {wurl_log1}%%{wurl_log2} ]" % cmi_debug )
        logging.info( f"%s - API endpoint #3: [ {self.premarket_url} ]" % cmi_debug )
        logging.info( f"%s - API endpoint #4: [ {self.info_url} ]" % cmi_debug )
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

    def learn_aclass(self, symbol):
        cmi_debug = __name__+"::"+self.learn_aclass.__name__+".#"+str(self.yti)
        logging.info( f"%s - Learn asset class using API endpoint: {self.info_url}" % cmi_debug )
        with self.js_session.get(self.info_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp1:
            logging.info( f"%s - Extract default guess data..." % cmi_debug )
            self.quote_json1 = json.loads(self.js_resp1.text)
            #figure out asset_class which defines which API endpoint to use...
            self.asset_class = -1
            t_info_url = "https://api.nasdaq.com/api/quote/" + self.symbol + "/info?assetclass="
            for i in ['stocks', 'etf']:
                test_info_url = t_info_url + i
                with self.js_session.get(test_info_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp4:
                    logging.info( f'%s - Test {symbol} for asset_class [ {i} ] @ API endpoint: {test_info_url}' % cmi_debug )
                    self.quote_json4 = json.loads(self.js_resp4.text)
                    if self.quote_json4['status']['rCode'] == 200:
                        self.asset_class = i
                        logging.info( f'%s - Asset_class is: [ {i} ] !' % cmi_debug )
                        break
                    else:
                        logging.info( f'%s - Asset_class is NOT: [ {i} ] !' % cmi_debug )
                        test_info_url = ""

        logging.info( f"%s - Done" % cmi_debug )
        return i    # asset_class identifier  (stocks / etf)

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
            logging.info( '%s - Stage #1 / Summary / get() data / storing...' % cmi_debug )
            self.quote_json1 = json.loads(self.js_resp1.text)
            logging.info( '%s - Stage #1 - Done' % cmi_debug )

        with self.js_session.get(self.watchlist_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp2:
            logging.info( '%s - Stage #2 / Watchlist / get() data / storing...' % cmi_debug )
            self.quote_json2 = json.loads(self.js_resp2.text)
            logging.info( '%s - Stage #2 - Done' % cmi_debug )

        with self.js_session.get(self.premarket_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp3:
            logging.info( '%s - Stage #3 / premarket / get() data / storing...' % cmi_debug )
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

# ###################################################################################################################################
# method 8
    def build_data(self):
        """
        Build-out the full quote data structure thats tidy & clean. All fields sourced from the extracted JSON dataset.
        """
        cmi_debug = __name__+"::"+self.build_data.__name__+".#"+str(self.yti)
        logging.info('%s - build quote data payload from JSON' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - prepare jsondata accessors [11/20/30]...' % cmi_debug )
        self.jsondata11 = self.quote_json1['data']                              # summary
        self.jsondata20 = self.quote_json2['data'][0]                           # watchlist
        self.jsondata30 = self.quote_json3['data']                              # premarket

        # Helper methods ##########################################################################################################
        """
        Private helper methods to poll nasdaq data model and test sanity for bad NULL data & bad/missing json keys
        NOTE: Keys & NULLs are somethimes bad becasue when the amrket is closed (e.g. premarket data). In that scenario
              this isn't an error scenario... but it's difficult logic to account for.
        Call before trying to access asdaq API json list indexes, as bad data will exert many hard errors.
        INFO: Checks 3 data zones in the nasdaq.com API json data model
              1. summary       :    self.jsondata11 = self.quote_json1['data']
              2. watchlist     :    self.jsondata20 = self.quote_json2['data'][0]
              3. pre-market    :    self.jsondata30 = self.quote_json3['data']
        """

        # ZONE #1 Summary zone....##############################################
        def nulls_summary():
            cmi_debug = __name__+"::"+nulls_summary.__name__+".#"+str(self.yti)
            logging.info( f'%s - probing json keys/fields for NULLs...' % cmi_debug )
            z = 1
            jd10_null_errors = 0
            jd_10s = ("PreviousClose", "MarketCap", "TodayHighLow", "AverageVolume", "OneYrTarget", "Beta", "FiftTwoWeekHighLow" )
            jd_10e = ("PreviousClose", "MarketCap", "TodayHighLow", "FiftyDayAvgDailyVol", "Beta", "FiftTwoWeekHighLow" )

            if self.asset_class == "stocks": jd_10 = jd_10s
            if self.asset_class == "etf": jd_10 = jd_10e

            try:
                y = self.jsondata11['summaryData']      # summary
            except TypeError:
                logging.info( f"%s - Probe #10 (summary): NULL data @: [data][summaryData]" % cmi_debug )
                jd10_null_errors = 1 + len(jd_10)       # everything in data set is BAD
                return jd10_null_errors
            except KeyError:
                logging.info( f"%s - Probe #10 (summary): NULL key @: [data][summaryData]" % cmi_debug )
                jd10_null_errors = 1 + len(jd_10)       # everything in data set is BAD
                return jd10_null_errors
            else:
                x = self.jsondata11['summaryData']
                for i in jd_10:
                    try:
                        y = x[i]
                    except TypeError:
                        logging.info( f"%s - Probe #10 (summary): NULL data @: [{i}]" % cmi_debug )
                        jd10_null_errors += 1
                    except KeyError:
                        logging.info( f"%s - Probe #10 (summary): NULL key @: [{i}]" % cmi_debug )
                        jd10_null_errors += 1
                    else:
                        z += 1
            logging.info( f"%s - NULL probe 10/11 (API=summary) / errors: {jd10_null_errors} / 7" % cmi_debug )
            return jd10_null_errors


        # ZONE #2 watchlist zone....############################################
        def nulls_watchlist():
            """
            This data zone is far more tollerant. keys/fields pre-exist. So this zone cant test for a
            non-existent/bad ticker symbol (or ETF/Fund). but this means errors are less severe.
            """
            cmi_debug = __name__+"::"+nulls_watchlist.__name__+".#"+str(self.yti)
            logging.info( f'%s - probing json keys/fields for NULLs...' % cmi_debug )
            z = 1
            x = self.jsondata20     # watchlist
            jd_20 = ("symbol", "companyName", "lastSalePrice", "netChange", "percentageChange", "deltaIndicator", "lastTradeTimestampDateTime", "volume" )
            jd20_null_errors = 0

            for i in jd_20:
                try:
                    y = x[i]
                except TypeError:
                    logging.info( f"%s - Probe #20 (watchlist): NULL data @: [{i}]" % cmi_debug )
                    jd20_null_errors += 1
                except KeyError:
                    logging.info( f"%s - Probe #20 (watchlist): NULL KEY data @: [{i}]" % cmi_debug )
                    jd20_null_errors += 1
                else:
                    z += 1
            logging.info( f"%s - NULL probe 20 (API=watchlist) / errors: {jd20_null_errors} / 8" % cmi_debug )
            return jd20_null_errors

            # ZONE #3 watchlist zone....########################################
        def nulls_premarket():
            cmi_debug = __name__+"::"+nulls_premarket.__name__+".#"+str(self.yti)
            logging.info( f'%s - probing json keys/fields for NULLs...' % cmi_debug )
            jd_31 = ("consolidated", "volume", "delta" )
            jd_30 = ("infoTable", "infoTable']['rows", "infoTable']['rows'][0", "infoTable']['rows'][0]['consolidated'",
                       "infoTable']['rows'][0]['volume'", "'infoTable']['rows'][0]['delta'" )
            z = 1
            jd31_null_errors = 0
            try:
                y = self.jsondata30['infoTable']['rows'][0]     # premarket
            except TypeError:
                logging.info( f"%s - Probe #30 (premarket): NULL data @: [infoTable][rows][0]" % cmi_debug )
                jd31_null_errors = 1 + len(jd_30)               # everything in data set is BAD
                return jd31_null_errors
            except KeyError:
                logging.info( f"%s - Probe #30 (premarket): NULL key @: [infoTable][rows][0]" % cmi_debug )
                jd31_null_errors = 1 + len(jd_30)               # everything in data set is BAD
                return jd31_null_errors
            else:
                x = self.jsondata30['infoTable']['rows'][0]
                for i in jd_31:
                    try:
                        y = x[i]
                    except TypeError:
                        logging.info( f"%s - Probe #31 (premarket): NULL data @: [{i}]" % cmi_debug )
                        jd31_null_errors += 1
                    except KeyError:
                        logging.info( f"%s - Probe #31 (premarket): NULL key @: [{i}]" % cmi_debug )
                        jd31_null_errors += 1
                    else:
                        z += 1
            logging.info( f"%s - NULL probe 30/31 (API=premarket): errors: {jd31_null_errors} / 6" % cmi_debug )
            return jd31_null_errors

################################################################################################
# Quote DATA extractor ########################################################################
################################################################################################
        wrangle_errors = 0
        null_count = 0
        a = nulls_summary()         # self.jsondata11 = self.quote_json1['data']
        b = nulls_watchlist()       # self.jsondata20 = self.quote_json2['data'][0]
        c = nulls_premarket()       # self.jsondata30 = self.quote_json3['data']

        if a == 0 and b == 0:    # GOOD - all data fields are available
            logging.info( f'%s - Nasdaq quote data is NOMINAL [ {a} {b} {c} ]' % cmi_debug )
            #
            # setup main JSON data zone accessors...
            #
            # WATCHLIST quote data
            if self.quote_json2['data'] is not None:                                # bad payload? - can also test b == 0
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
            if self.quote_json3['data'] is not None:                                # bad payload? - can also test c == 0
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
                    open_price = jsondata31['consolidated']                             # WARN: open_price info = multi-field string needs splitting e.g. "$140.8 +1.87 (+1.35%)"
                    open_volume = jsondata31['volume']                                  # e.g. "71,506"
                    open_updown = jsondata31['delta']                                   # e.g. "up"
                    logging.info( '%s - Stage #2 / [3] fields - Done' % cmi_debug )
            else:
                logging.info('%s - Stage #2 / zone [data] NULL json payload - NOT regular stock' % cmi_debug )        # bad symbol json payload
                self.quote.clear()
                wrangle_errors += -1

            # SUMMARY quote data
            if self.quote_json1['data'] is not None:                                # bad payload? - can also test a == 0
                logging.info('%s - Stage #3 / Accessing data fields...' % cmi_debug )
                jsondata10 = self.quote_json1['data']['summaryData']                # HEAD of data payload
                prev_close = jsondata10['PreviousClose']['value']                   # e,g, "$138.93"
                mkt_cap = jsondata10['MarketCap']['value']                          # e.g. "128,460,592,862"
                today_hilo = jsondata10['TodayHighLow']['value']                    # WARN: multi-field string needs splitting/wrangeling e.g. "$143.97/$140.37"
                #
                if self.asset_class == "stocks":
                    avg_vol = jsondata10['AverageVolume']['value']                      # e.g. "4,811,121" or N/A
                    oneyear_target = jsondata10['OneYrTarget']['value']                 # e.g. "$151.00"
                else:
                    avg_vol = jsondata10['FiftyDayAvgDailyVol']['value']                      # e.g. "4,811,121" or N/A
                    oneyear_target = 0                 # e.g. "$151.00
                #
                beta = jsondata10['Beta']['value']                                  # e.g. 1.23
                LII_week_hilo = jsondata10['FiftTwoWeekHighLow']['value']           # WARN: multi-field string needs splitting/wrangeling e.g. "$152.84/$105.92"
                logging.info( '%s - Stage #3 / [7] fields - Done' % cmi_debug )
            else:
                logging.info('%s - Stage #2 / NULL json payload - NOT regular stock' % cmi_debug )        # bad symbol json payload
                self.quote.clear()
                wrangle_errors += -1

            ########################################################################################
            # wrangle, clean, cast & prepare the data ##############################################
            logging.info('%s - Begin heavy data wrangle workloads...' % cmi_debug )

            # >>> debug helper support <<<
            #
            def f_xray(template):
                z = template
                y = f"'{template}'"
                #h = f"'{y}'"
                print ( f"Incomming: template: {template}" )
                print ( f"Incomming: y_template: {y}" )
                ouz = eval(z)
                ouy = eval(y)
                print ( f">>> ouy: {ouy} <<< / >> oua: {ouz} << / >>> y: {y} << / >>> z: {z} <<< ")
                return out

            template_a = "List key: {name}"
            kc = 0
            working_on = [co_sym, co_name, price, price_net, price_pct, arrow_updown ]
            #working_on = ['co_sym', 'co_name', 'price', 'price_net', 'price_pct', 'arrow_updown' ]
            #        price_timestamp, vol_abs, open_price, open_volume, open_updown, \
            #        prev_close, mkt_cap, today_hilo, avg_vol, oneyear_target, beta, \
            #        LII_week_hilo]
            for name in working_on:
                print ( f"{f_xray(name)} / {name}" )

            #
            #
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
            """
            Open_price data elements are 3 fields concatinted into 1 long string / e.g. $140.8 +1.87 (+1.35%)
            This is a bad nasdaq strategy. We must split & post-process/wrangle the split fields
            """
            if open_price == "N/A" or open_price is None:
                """ Stage #0 """
                logging.info( f'%s - BAD open_price compound data: {type(open_price)} / {open_price} / set all to 0.0' % cmi_debug )
                open_price_cl = np.float(0)
                open_price_net = float(0)
                open_price_pct_cl = float(0)
                wrangle_errors += 3
            else:       # data is good...access 3 indices of sub-data from split list[]
                ops = open_price.split()
                logging.info( f"%s - Split open_price into {len(ops)} fields" % cmi_debug )

                """ Stage #1 """
                try:
                    open_price = ops[0]                     # e.g. 140.8
                except IndexError:
                    logging.info( f'%s - Bad key open_price: {type(open_price)} / setting to $0.0 / {open_price}' % cmi_debug )
                    open_price = float(0)
                    wrangle_errors += 1
                except ValueError:
                    logging.info( f'%s - Bad open_price: {type(open_price)} / setting to $0.0 / {open_price}' % cmi_debug )
                    open_price = float(0)
                    wrangle_errors += 1
                else:
                    open_price_cl = (re.sub('[ $,]', '', ops[0]))   # remove " " $ ,
                    open_price_cl = np.float(open_price_cl)
                    """ Stage #2 """

                    if len(ops) != 1:   # the split failed to seperate all 3 elements. i.e. there open_price_net & open_price_pct don't exist
                        try:    # data is good...keep processing...
                            open_price_net = ops[1]                 # (test for missing data) - good data =  +1.87
                        except IndexError:
                            logging.info( f'%s - Bad key open_price_net: {type(open_price_net)} / setting to $0.0 / {open_price_net}' % cmi_debug )
                            open_price_net = float(0)               # set NULL data to ZERO
                            wrangle_errors += 1
                        except ValueError:
                            logging.info( f'%s - Bad open_price_net: {type(open_price_net)} / setting to $0.0 / {open_price_net}' % cmi_debug )
                            open_price_net = float(0)               # set NULL data to ZERO
                            wrangle_errors += 1
                        except TypeError:
                            logging.info( f'%s - Bad open_price_net: {type(open_price_net)} / setting to $0.0 / {open_price_net}' % cmi_debug )
                            open_price_net = float(0)               # set NULL data to ZERO
                            wrangle_errors += 1
                        else:
                            pass    # data is good...keep processing...
                            # INFO: no need of clean open_price_net - VAR is currently not used n our data model
                            """ Stage #3 """
                            try:
                                open_price_pct = ops[2]                 # (test for missing data) - good data = e.g. (+1.35%)"
                            except IndexError:
                                logging.info( f'%s - Bad key open_price_pct: {type(open_price_pct)} / setting to $0.0 / {open_price_pct}' % cmi_debug )
                                open_price_pct = float(0)               # set NULL data to ZERO
                                wrangle_errors += 1
                            except ValueError:
                                logging.info( f'%s - Bad open_price_pct: {type(open_price_pct)} / setting to $0.0 / {open_price_pct}' % cmi_debug )
                                open_price_pct = float(0)               # set NULL data to ZERO
                                wrangle_errors += 1
                            else:
                                open_price_pct_cl = (re.sub('[)(%]', '', price_pct))        # # remove " ", %  (leave +/- indicator)
                                # INFO: no need of clean open_price_net - VAR is currently not used n our data model
                                logging.info( f"%s - All 3 open_price vars sucessfully split & processed" % cmi_debug )
                    else:
                        open_price_net = float(0)
                        open_price_pct_cl = float(0)

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

            ####################################################################
            # craft final data structure.
            # NOTE: globally accessible and used by quote DF and quote DICT
            symbol=co_sym_lj.rstrip()
            logging.info( f"%s - Build global Dataframe list: {symbol}" % cmi_debug )        # so we can access it natively if needed, without using pandas
            self.data0 = [[ \
               co_sym_lj, \
               co_name_lj, \
               arrow_updown, \
               np.float(price_cl), \
               price_net_cl, \
               price_pct_cl, \
               open_price_cl, \
               np.float(prev_close_cl), \
               np.float(vol_abs_cl), \
               mkt_cap_cl, \
               price_timestamp, \
               time_now ]]

            # craft the quote DICT. Doesn't hurt to do this here as it assumed that the data
            # is all nice & clean & in its final beautiful shape by now.
            symbol=co_sym_lj.rstrip()
            logging.info( f"%s - Build global dict: {symbol}" % cmi_debug )        # so we can access it natively if needed, without using pandas
            self.quote = dict( \
                symbol=co_sym_lj.rstrip(), \
                name=co_name, \
                updown=arrow_updown, \
                cur_price=price_cl, \
                prc_change=price_net_cl, \
                pct_change=price_pct_cl, \
                open_price=open_price_cl, \
                open_price_net=open_price_net, \
                open_price_pct=open_price_pct_cl, \
                prev_close=prev_close_cl, \
                vol=vol_abs_cl, \
                avg_vol=avg_vol, \
                one_year_target=oneyear_target, \
                beta=beta, \
                oneyear_hilo=LII_week_hilo, \
                mkt_cap=mkt_cap_cl )

            return wrangle_errors
        else:
            wrangle_errors += 50
            logging.info( f"%s - Nasdaq quote data is ABERRANT [ {a} {b} {c} ]" % cmi_debug )

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
