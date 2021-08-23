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

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class un_volumes:
    """Class to discover unusual volume data from NASDAQ.com data source"""

    # global accessors
    up_df0 = ""             # DataFrame - Full list of Unusual UP volume
    down_df1 = ""           # DataFrame - Full list of Unusual DOWN volume
    df2 = ""                # DataFrame - List of Top 10 (both UP & DOWN
    uvol_all_data =""       # JSON dataset contains ALL data
    uvol_up_data =""        # JSON dataset contains UP data only
    uvol_down_data =""      # JSON dataset contains DOWN data only
    yti = 0                 # Unique instance identifier
    cycle = 0               # class thread loop counter
    soup = ""               # BS4 shared handle between UP & DOWN (1 URL, 2 embeded data sets in HTML doc)
    args = []               # class dict to hold global args being passed in from main() methods

                            # NASDAQ.com header/cookie hack
    nasdaq_headers = { \
                    'authority': 'api.nasdaq.com', \
                    'path': '/api/quote/list-type/unusual_volume', \
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
        self.up_df0 = pd.DataFrame(columns=[ 'Row', 'Co_symbol', 'Co_name', 'Price', 'Net_change', 'Prc_pct', "Vol", 'Vol_pct', 'Time' ] )
        self.down_df1 = pd.DataFrame(columns=[ 'Row', 'Co_symbol', 'Co_name', 'Price', 'Net_change', 'Prc_pct', "Vol", 'Vol_pct', 'Time' ] )
        self.df2 = pd.DataFrame(columns=[ 'ERank', 'Co_symbol', 'Co_name', 'Price', 'Net_change', 'Prc_pct', "Vol", 'Vol_pct', 'Time' ] )
        self.yti = yti
        self.js_session = HTMLSession()                        # init JAVAScript processor early
        self.js_session.cookies.update(self.nasdaq_headers)    # load cookie/header hack data set into session
        return

# method #1
    def get_un_vol_data(self):
        """Access NEW nasdaq.com JAVASCRIPT page [unusual volume] and extract the native JSON dataset"""
        """JSON dataset contains *BOTH* UP vol & DOWN vol for top 25 symbols, right now!"""
        """NO BeautifulSOup scraping needed anymore. We access the pure JSON datset via native API rest call"""
        """note: Javascript engine is required, Cant process/read a JS page via requests(). The get() hangs forever"""

        cmi_debug = __name__+"::"+self.get_un_vol_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        # present ourself to NASDAQ.com so we can extract the critical cookie -> ak_bmsc
        logging.info('%s - blind get()' % cmi_debug )
        self.js_resp0 = self.js_session.get("https://www.nasdaq.com" )

        # render the extracted js webpage in our js engine processor
        # initial get() is denided by NASDAQ.com as unauthourised. *BUT* we are issued the critical 'ak_bmsc' cookie in the deny response
        logging.info('%s - JS engine render' % cmi_debug )
        self.js_resp0.html.render()  # might be able to not do this. DO I really need to render() for the initial fake/blind get?

        # NASDAQ cookie hack
        logging.info('%s - EXTRACT/INSERT valid cookie  ' % cmi_debug )
        self.js_session.cookies.update({'ak_bmsc': self.js_session.cookies['ak_bmsc']} )

        # no BeautifulSoup scraping needed...
        # we can access pure 'Unusual VOlume' JSON data via an authenticated/valid REST API call
        logging.info('%s - API JSON read' % cmi_debug )
        self.js_resp2 = self.js_session.get("https://api.nasdaq.com/api/quote/list-type/unusual_volume")
        logging.info('%s - data extracted' % cmi_debug )

        logging.info('%s - store JSON datasets ' % cmi_debug )   # store JSON datasets
        logging.info('%s - store ALL' % cmi_debug )
        self.uvol_all_data = json.loads(self.js_resp2.text)
        logging.info('%s - store UP' % cmi_debug )
        self.uvol_up_data =  self.uvol_all_data['data']['up']['table']['rows']
        logging.info('%s - store DOWN' % cmi_debug )
        self.uvol_down_data = self.uvol_all_data['data']['down']['table']['rows']

         # Xray DEBUG 
        if self.args['bool_xray'] is True:
            print ( f"================================ {self.yti} ======================================" )
            print ( f"=== session cookies ===\n" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )

            print ( " " )
            print ( f"=== response cookies ===\n" )
            for j in self.js_resp2.cookies.items():
                print ( f"{j}" )

        return



# method #2
# New method to build a Pandas DataFrame from JSON data structure
    def build_df(self, ud):
        """Build-out a fully populated Pandas DataFrame containg the"""
        """key fields from the JSON dataset"""
        """Wrangle, clean/convert/format the data correctly."""
        """calling arg: ud  (up_volume = 0 / down_volume = 1)"""

        this_df = ""
        cmi_debug = __name__+"::"+self.build_df.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        if ud == 0:
            logging.info('%s - build UP df' % cmi_debug )
            this_df = self.up_df0
            dataset = self.uvol_up_data
        elif ud == 1:
            logging.info('%s - build DOWN df' % cmi_debug )
            this_df = self.down_df1
            dataset = self.uvol_down_data
        else:
            logging.info('%s - Error: invalid dataframe. EXITING' % cmi_debug )
            return 0

        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop all rows from DF' % cmi_debug )
        this_df.drop(this_df.index, inplace=True)

        x = 1    # row counter Also leveraged for unique dataframe key
        for json_data_row in dataset:     # genrator object
            co_sym = json_data_row['symbol']
            co_name = json_data_row['company']
            price = json_data_row['lastSale']
            price_net = json_data_row['netChange']
            arrow_updown = json_data_row['deltaIndicator']
            price_pct = json_data_row['percentChange']
            vol_abs = json_data_row['shareVolume']
            vol_pct = json_data_row['volumePctChange']

            # COL NAME     variable       final varable cleansed
            # ==================================================
            # Row        = x              x
            # Co_symbol  = co_sym         co_sym_lj
            # Co_name    = co_name        co_name_lj
            # Price      = price          price_cl
            # Net_change = price_net      price_net_cl
            # Prc_pct    = price_pct      price_pct_cl
            # vol        = vol_abs        vol_abs_cl
            # vol_pct    = vol_pct        vol_pct_cl
            # Time       = time_now       time_now

            # wrangle, clean, cast & prepare the data
            co_sym_lj = np.array2string(np.char.ljust(co_sym, 6) )         # left justify TXT in DF & convert to raw string
            co_name_lj = (re.sub('[\'\"]', '', co_name) )                  # remove " ' and strip leading/trailing spaces
            co_name_lj = np.array2string(np.char.ljust(co_name_lj, 25) )   # left justify TXT in DF & convert to raw string
            co_name_lj = (re.sub('[\']', '', co_name_lj) )                 # remove " ' and strip leading/trailing spaces

            price_cl = (re.sub('[ $,]', '', price))                        # remove $ sign
            price_net_cl = (re.sub('[\-+]', '', price_net))                # remove - + signs
            price_pct_cl = (re.sub('[\-+%]', '', price_pct))               # remove - + % signs
            vol_abs_cl = (re.sub('[,]', '', vol_abs))                      # remove ,
            vol_pct_cl = (re.sub('[%]', '', vol_pct))                      # remover %

            self.data0 = [[ \
                       x, \
                       re.sub('\'', '', co_sym_lj), \
                       co_name_lj, \
                       np.float(price_cl), \
                       np.float(price_net_cl), \
                       np.float(price_pct_cl), \
                       np.float(vol_abs_cl), \
                       np.float(vol_pct_cl), \
                       time_now ]]

            if ud == 0:
                logging.info('%s - append UP Volume data into DataFrame' % cmi_debug )
                self.temp_df0 = pd.DataFrame(self.data0, columns=[ 'Row', 'Co_symbol', 'Co_name', 'Price', 'Net_change', 'Prc_pct', "Vol", 'Vol_pct', 'Time' ], index=[x] )
                self.up_df0 = self.up_df0.append(self.temp_df0, sort=False)    # append this ROW of data into the REAL DataFrame
            else:
                logging.info('%s - append DOWN Volume data into DataFrame' % cmi_debug )
                self.temp_df1 = pd.DataFrame(self.data0, columns=[ 'Row', 'Co_symbol', 'Co_name', 'Price', 'Net_change', "Prc_pct", "Vol", 'Vol_pct', 'Time' ], index=[x] )
                self.down_df1 = self.down_df1.append(self.temp_df1, sort=False)    # append this ROW of data into the REAL DataFrame

            x += 1

        logging.info('%s - populated new DF' % cmi_debug )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)
                        # sucess = lobal class accessor (y_toplosers.df0) populated & updated


# method #3
    def up_unvol_listall(self):
        """Print the full DataFrame table list of NASDAQ unusual UP volumes"""
        """Sorted by % Change"""
        logging.info('ins.#%s.up_unvol_listall() - IN' % self.yti )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.up_df0.sort_values(by='Prc_pct', ascending=False ) )
        logging.info('ins.#%s.up_unvol_listall() - DONE' % self.yti )
        return

# method #4
    def down_unvol_listall(self):
        """Print the full DataFrame table list of NASDAQ unusual DOWN volumes"""
        """Sorted by % Change"""
        logging.info('ins.#%s.down_unvol_listall() - IN' % self.yti )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.down_df1.sort_values(by='Prc_pct', ascending=False ) )
        logging.info('ins.#%s.down_unvol_listall() - DONE' % self.yti )
        return
