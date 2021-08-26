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
    quote_pridata = ""      # JSON structured dataset contains ALL data
    yti = 0                 # Unique instance identifier
    cycle = 0               # class thread loop counter
    args = []               # class dict to hold global args being passed in from main() methods
    js_resp0 = ''           # session response handle for initial blind get()
    js_resp2 = ''           # session response handle for main json data get()
    quote_url = ""
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
        logging.info('%s - INIT' % cmi_debug )
        # init empty DataFrame with preset colum names
        self.args = global_args                                # Only set once per INIT. all methods are set globally
        self.quote_df0 = pd.DataFrame(columns=[ 'Symbol', 'Co_name', 'arrow_updown', 'Cur_price', 'Prc_change', 'Pct_change', 'Open_price', 'Prev_close', 'Vol', 'Mkt_cap', 'Exch_timestamp', 'Time' ] )
        self.yti = yti
        self.js_session = HTMLSession()                        # init JAVAScript processor early
        self.js_session.cookies.update(self.nasdaq_headers)    # load cookie/header hack data set into session
        return

# method 4
    def update_headers(self, symbol):
        cmi_debug = __name__+"::"+self.update_headers.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        self.symbol = symbol
        logging.info('%s - set cookies/headers (path:) object to endpoint' % cmi_debug )
        self.path = '/api/quote/' + self.symbol + '/info?assetclass=stocks'
        #self.nasdaq_headers['path'] = self.path
        self.js_session.cookies.update({'path': self.path} )
        logging.info('cookies/headers path: object endpoint is - %s' % self.path )

        return

# method 6
    def init_blind_session(self):
        cmi_debug = __name__+"::"+self.init_blind_session.__name__+".#"+str(self.yti)
        # note: we ping www.nasdaq.com. No need for a API specific url. That comes later.
        # assumes the cookies have already been set up

        with self.js_session.get('https://www.nasdaq.com', stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - extract & update GOOD cookie  ' % cmi_debug )
            #self.js_session.cookies.update({'ak_bmsc': self.js_resp0.cookies['ak_bmsc']} )    # NASDAQ cookie hack

        # if the get() succeds, the response handle is automatically saved in Class Global accessor -> self.js_resp0
        return

# method 7
    def init_dummy_session(self):
        cmi_debug = __name__+"::"+self.init_dummy_session.__name__+".#"+str(self.yti)
        # note: we ping www.nasdaq.com.
        #  No need for a API specific url. That comes later.

        with self.js_session.get('https://www.nasdaq.com', stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - extract & update GOOD cookie  ' % cmi_debug )
            self.js_session.cookies.update({'ak_bmsc': self.js_resp0.cookies['ak_bmsc']} )    # NASDAQ cookie hack

        # if the get() succeds, the response handle is automatically saved in Class Global accessor -> self.js_resp0
        return

# method 6
    def form_api_endpoint(self, symbol):
        cmi_debug = __name__+"::"+self.form_api_endpoint.__name__+".#"+str(self.yti)
        logging.info('%s - form API endpoint for json get' % cmi_debug )
        self.quote_url = 'https://api.nasdaq.com' + self.path
        logging.info('API url get endpoint is: %s' % self.quote_url )
        self.quote_url = self.quote_url

        return

# method #1
    def get_nquote(self, symbol):
        """Access NEW nasdaq.com JAVASCRIPT page [unusual volume] and extract the native JSON dataset"""
        """JSON dataset contains *BOTH* UP vol & DOWN vol for top 25 symbols, right now!"""
        """NO BeautifulSOup scraping needed anymore. We access the pure JSON datset via native API rest call"""
        """note: Javascript engine is required, Cant process/read a JS page via requests(). The get() hangs forever"""

        cmi_debug = __name__+"::"+self.get_nquote.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        self.symbol = symbol

        # Initial blind get
        # present ourself to NASDAQ.com so we can extract the critical cookie -> ak_bmsc
        # be nice and set a healthy cookie package
        #logging.info('%s - set cookies/headers path: object endpoint' % cmi_debug )
        #self.path = '/api/quote/' + self.symbol + '/info?assetclass=stocks'
        #self.nasdaq_headers['path'] = self.path
        #logging.info('cookies/headers path: object endpoint is - %s' % self.path )

        #logging.info('%s - blind get()' % cmi_debug )
        #with self.js_session.get('https://www.nasdaq.com', stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp0:
        #    logging.info('%s - EXTRACT/INSERT valid cookie  ' % cmi_debug )
        #    self.js_session.cookies.update({'ak_bmsc': self.js_resp0.cookies['ak_bmsc']} )    # NASDAQ cookie hack

        # 2nd get with the secret nasdaq.com cookie no inserted
        #logging.info('%s - PREP for rest API json get' % cmi_debug )
        #self.quote_url = 'https://api.nasdaq.com' + self.path
        #logging.info('API url get endpoint: %s' % self.quote_url )

        with self.js_session.get(self.quote_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp2:
            # read the webpage with our Javascript engine processor
            logging.info('%s - Javascript engine processing...' % cmi_debug )
            self.js_resp2.html.render()
            logging.info('%s - Javascript engine completed!' % cmi_debug )

            # access pure 'stock quote' JSON data via an authenticated/valid REST API call
            logging.info('%s - json data extracted' % cmi_debug )
            logging.info('%s - store FULL json dataset' % cmi_debug )
            self.quote_pridata = json.loads(self.js_resp2.text)


         # Xray DEBUG 
        if self.args['bool_xray'] is True:
            print ( f"================================ {self.yti} ======================================" )
            print ( f"=== session cookies ===\n" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )

        return

# method #2
# New method to build a Pandas DataFrame from JSON data structure
    def build_df(self):
        """Build-out a fully populated Pandas DataFrame containg the"""
        """key fields from the JSON dataset"""
        """Wrangle, clean/convert/format the data correctly."""
        """calling arg: ud  (up_volume = 0 / down_volume = 1)"""

        cmi_debug = __name__+"::"+self.build_df.__name__+".#"+str(self.yti)
        logging.info('%s - build quote df from JSON' % cmi_debug )

        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop ephemeral DF' % cmi_debug )
        self.quote_df0.drop(self.quote_df0.index, inplace=True)

        logging.info('%s - insert json fields into df' % cmi_debug )
        jsondata = self.quote_pridata['data']
        print ( f"DEBUG: {jsondata}" )
        co_sym = jsondata['symbol']
        co_name = jsondata['companyName']
        price = jsondata['primaryData']['lastSalePrice']
        price_net = jsondata['primaryData']['netChange']
        price_pct = jsondata['primaryData']['percentageChange']
        arrow_updown = jsondata['primaryData']['deltaIndicator']
        price_timestamp = jsondata['primaryData']['lastTradeTimestamp']
        vol_abs = jsondata['keyStats']['Volume']['value']
        prev_close = jsondata['keyStats']['PreviousClose']['value']
        open_price = jsondata['keyStats']['OpenPrice']['value']
        mkt_cap = jsondata['keyStats']['MarketCap']['value']

        # COL NAME     variable       final varable cleansed
        # ==================================================
        # Symbol          = co_sym           co_sym_lj
        # Co_name         = co_name          co_name_lj
        # arrow_updown    = arrow_updown     arrow_updown
        # Cur_price       = price            price_cl
        # Prc_change      = price_net        price_net_cl
        # Pct_change      = price_pct        price_pct_cl
        # vol             = open_price       openprice_cl
        # prev_close      = prev_close       prev_close_cl
        # vol_abs         = vol_abs          vol_abs_cl
        # mkt_cap         = mkt_cap          mkt_cap_cl
        # price_timestamp = price_timestamp  timestamp_cl

        # wrangle, clean, cast & prepare the data
        logging.info('%s - Clean wrangle cast prep data' % cmi_debug )
        co_sym_lj = np.array2string(np.char.ljust(co_sym, 6) )         # left justify TXT in DF & convert to raw string
        co_name_lj = (re.sub('[\'\"]', '', co_name) )                  # remove " ' and strip leading/trailing spaces
        co_name_lj = np.array2string(np.char.ljust(co_name_lj, 25) )   # left justify TXT in DF & convert to raw string
        co_name_lj = (re.sub('[\']', '', co_name_lj) )                 # remove " ' and strip leading/trailing spaces


        if price == "N/A":
            price_cl = 0
            logging.info('%s - Found bad N/A data' % cmi_debug )
        else:
            price_cl = (re.sub('[ $,]', '', price))                    # remove $ sign

        if price_net == "N/A":
            price_net_cl = 0
            logging.info('%s - Found bad N/A data' % cmi_debug )
        elif price_net == 'UNCH':
            price_net_cl = "Unch"
            logging.info('%s - Found unchanged price flag' % cmi_debug )
        else:
            price_net_cl = (re.sub('[\-+]', '', price_net))                # remove - + signs
            price_net_cl = np.float(price_net)

        if price_pct == "N/A":
            price_pct_cl = 0
            logging.info('%s - Found bad N/A data' % cmi_debug )
        elif price_pct == "UNCH":
            price_pct_cl = "Unch"
            logging.info('%s - Found unchanged price flag' % cmi_debug )
        elif price_pct == '':
            price_pct_cl = "No data"
        else:
            print ( f"DEBUG: price_pct: {price_pct}" )
            price_pct = (re.sub('[\-+%]', '', price_pct))               # remove - + % signs
            price_pct_cl = np.float(price_pct)

        if open_price == "N/A":
            open_price_cl = 0
            logging.info('%s - Found bad N/A data' % cmi_debug )
        else:
            open_price_cl = (re.sub('[ $,]', '', open_price))               # remove $ sign

        if prev_close == "N/A":
            prev_close_cl = 0
            logging.info('%s - Found bad N/A data' % cmi_debug )
        else:
            prev_close_cl = (re.sub('[ $,]', '', prev_close))              # remove $ sign

        if mkt_cap == "N/A":
            mkt_cap_cl = 0
            logging.info('%s - Found bad N/A data' % cmi_debug )
        else:
            mkt_cap_cl = (re.sub('[,]', '', mkt_cap))                      # remove ,

        vol_abs_cl = (re.sub('[,]', '', vol_abs))                      # remove ,
        timestamp_cl = (re.sub('[DATA AS OF ]', '', price_timestamp) )    # remove prefix string "DATA AS OF " 

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
                   np.float(mkt_cap_cl), \
                   timestamp_cl, \
                   time_now ]]

        #logging.info('%s - create quote DataFrame' % cmi_debug )
        #self.quote_df0 = pd.DataFrame(self.data0, columns=[ 'Symbol', 'Co_name', 'arrow_updown', 'Cur_price', 'Prc_change', 'Pct_change', 'Open_price', 'Prev_close', 'Vol', 'Mkt_cap', 'Exch_timestamp', 'Time' ] )

        #logging.info('%s - populated new DF' % cmi_debug )

        logging.info('%s - Build quote dict' % cmi_debug )                        # so we can access it natively if needed, without using pandas
        self.quote = dict( \
                symbol=co_sym_lj, \
                name=co_name, \
                updown=arrow_updown, \
                cur_price=price_cl, \
                prc_change=price_net_cl, \
                pct_change=price_pct_cl, \
                open_price=open_price_cl, \
                prev_close=prev_close_cl, \
                vol=vol_abs_cl, \
                mkt_cap=mkt_cap_cl )

        return
