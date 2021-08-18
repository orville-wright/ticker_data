#!/usr/bin/python3
#import urllib
#import urllib.request
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
    uvol_json_data =""      # JSON dataset contains both UP & DOWN data
    up_table_data = ""      # DEPRICATED - BS4 constructor object of HTML <table> sub-doc > UP vol data
    down_table_data = ""    # DEPRICATED - BS4 constructor object of HTML <table> sub-doc > DOWN vol data
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


    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INIT' % cmi_debug )
        # init empty DataFrame with preset colum names
        self.up_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Vol', 'Vol_pct', 'Time'] )
        self.down_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Vol', 'Vol_pct', 'Time'] )
        self.df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Vol', 'Vol_pct', 'Time'] )
        self.yti = yti
        # init JAVAScript processor early
        self.js_session = HTMLSession()
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
        self.js_resp0 = self.js_session.get("https://www.nasdaq.com" )

        # render the extracted js webpage in our js engine processor
        # initial get() is denided by NASDAQ.com as unauthourised. *BUT* we are issued the critical 'ak_bmsc' cookie in the deny response
        logging.info('%s - JS engine render' % cmi_debug )
        self.js_resp0.html.render()

        # NASDAQ cookie hack
        logging.info('%s - INSERT session cookie/headers  ' % cmi_debug )
        self.js_session.cookies.update({'ak_bmsc': self.js_session.cookies['ak_bmsc']} )

        # no BeautifulSoup scraping needed...
        # we can access pure 'Unusual VOlume' JSON data via an authenticated/valid REST API call
        logging.info('%s - API JSON read' % cmi_debug )
        self.js_resp2 = self.js_session.get("https://api.nasdaq.com/api/quote/list-type/unusual_volume")
        logging.info('%s - data extracted' % cmi_debug )

        logging.info('%s - store JSON dataset ' % cmi_debug )   # store as pure JSON
        self.uvol_json_data = json.loads(self.js_resp2.text)
        logging.info('%s - JSON payload ' % cmi_debug )
        
        # HACKING...
        #print ( self.js_resp2.text )
        for c in range (0,25):
            print ( self.uvol_json_data['data']['up']['table']['rows'][c] )

        for c in range (0,25):
            print ( self.uvol_json_data['data']['down']['table']['rows'][c] )

        return

# method #2
    def get_downonuvol_data(self):
        """Connect to old.nasdaq.com and extract (scrape) the raw HTML string data from"""
        """the embedded html data table [DOWN_on_unusual_vol ]. Returns a BS4 handle."""

        cmi_debug = __name__+"::"+self.get_downonuvol_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        if not self.soup:
            logging.info('%s - BS4 object empty: Constructing now' % cmi_debug )
            with urllib.request.urlopen("https://old.nasdaq.com/markets/unusual-volume.aspx") as url:
                s = url.read()
                logging.info('%s - open url, read in html stream & parse' % cmi_debug )
                self.soup = BeautifulSoup(s, "html.parser")
                logging.info('%s - save BS4 class data object' % cmi_debug )
                self.all_tagid_down = self.soup.find( id="_down" )           # locate the section with ID = '_down' > output RAW htnml
                self.down_table_data = self.all_tagid_down.table             # move into the <table> section > ouput RAW HTML
                self.down_table_rows = ( tr_row for tr_row in ( self.down_table_data.find_all( 'tr' ) ) )      # build a generator of <tr> objects
                logging.info('%s - close url handle' % cmi_debug )
                url.close()
        else:
            logging.info('%s - BS4 object cached, re-use hot data. No network op' % cmi_debug )      # this might not be a good idea !!
            self.all_tagid_down = self.soup.find( id="_down" )           # locate the section with ID = '_down' > output RAW htnml
            self.down_table_data = self.all_tagid_down.table             # move into the <table> section > ouput RAW HTML
            self.down_table_rows = ( tr_row for tr_row in ( self.down_table_data.find_all( 'tr' ) ) )      # build a generator of <tr> objects
        # other HTML accessor methods - good for reference
        #self.up_table_rows = self.up_table_data.find_all( "tr")
        #self.up_table_rows = self.up_table_data.tr
        #self.up_table_rows2 = self.up_table_data.td
        logging.info('%s - DONE' % cmi_debug )
        return

# method #3
    def up_unvol_listall(self):
        """Print the full DataFrame table list of NASDAQ unusual UP volumes"""
        """Sorted by % Change"""
        logging.info('ins.#%s.up_unvol_listall() - IN' % self.yti )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.up_df0.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built
        logging.info('ins.#%s.up_unvol_listall() - DONE' % self.yti )
        return

# method #4
    def down_unvol_listall(self):
        """Print the full DataFrame table list of NASDAQ unusual DOWN volumes"""
        """Sorted by % Change"""
        logging.info('ins.#%s.down_unvol_listall() - IN' % self.yti )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.down_df0.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built
        logging.info('ins.#%s.down_unvol_listall() - DONE' % self.yti )
        return

# method #6
# New method to build a Pandas DataFrame from JSON data structure

# method #5
    def build_df(self, ud):
        """Build-out a fully populated Pandas DataFrame containg all the"""
        """extracted/scraped fields from the html/markup table data"""
        """Wrangle, clean/convert/format the data correctly."""
        """calling arg: ud  (up_volume = 0 / down_volume = 1)"""

        this_df = ""
        cmi_debug = __name__+"::"+self.build_df.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        if ud == 0:
            logging.info('%s - UP volume analysis' % cmi_debug )
            this_df = self.up_df0
            table_section = self.up_table_rows
        elif ud == 1:
            logging.info('%s - DOWN volume analysis' % cmi_debug )
            this_df = self.down_df0
            table_section = self.down_table_rows
        else:
            logging.info('%s - Error: invalid dataframe. EXITING' % cmi_debug )
            return 0

        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop all rows from DataFrame' % cmi_debug )
        this_df.drop(this_df.index, inplace=True)

        x = 1    # row counter Also leveraged for unique dataframe key
        col_headers = next(table_section)     # ignore the 1st TR row object, which is column header titles
        for tr_data in table_section:     # genrator object
            extr_strings = tr_data.stripped_strings
            co_sym = next(extr_strings)
            co_name = next(extr_strings)
            price = next(extr_strings)
            price_net = next(extr_strings)
            arrow_updown = next(extr_strings)
            price_pct = next(extr_strings)
            vol_abs = next(extr_strings)
            vol_pct = next(extr_strings)

            # wrangle & clean the data
            co_sym_lj = np.array2string(np.char.ljust(co_sym, 6) )      # left justify TXT in DF & convert to raw string

            co_name_lj = (re.sub('[\'\"]', '', co_name) )    # remove " ' and strip leading/trailing spaces
            co_name_lj = np.array2string(np.char.ljust(co_name_lj, 25) )   # left justify TXT in DF & convert to raw string
            co_name_lj = (re.sub('[\']', '', co_name_lj) )    # remove " ' and strip leading/trailing spaces

            price_cl = (re.sub('[ $,]', '', price))
            price_pct_cl = (re.sub('[\-+%]', '', price_pct))
            vol_abs_cl = (re.sub('[,]', '', vol_abs))
            vol_pct_cl = (re.sub('[%]', '', vol_pct))

            self.data0 = [[ \
                       x, \
                       re.sub('\'', '', co_sym_lj), \
                       co_name_lj, \
                       np.float(price_cl), \
                       np.float(price_net), \
                       np.float(price_pct_cl), \
                       np.float(vol_abs_cl), \
                       np.float(vol_pct_cl), \
                       time_now ]]

            if ud == 0:
                logging.info('%s - append UP Volume data into DataFrame' % cmi_debug )
                self.temp_df0 = pd.DataFrame(self.data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', "Vol", 'Vol_pct', 'Time' ], index=[x] )
                self.up_df0 = self.up_df0.append(self.temp_df0, sort=False)    # append this ROW of data into the REAL DataFrame
            else:
                logging.info('%s - append DOWN Volume data into DataFrame' % cmi_debug )
                self.temp_df1 = pd.DataFrame(self.data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', "Vol", 'Vol_pct', 'Time' ], index=[x] )
                self.down_df0 = self.down_df0.append(self.temp_df1, sort=False)    # append this ROW of data into the REAL DataFrame

            # DEBUG
            if self.args['bool_xray'] is True:        # DEBUG
                print ( "================================", x, "======================================")
                print ( co_sym, co_name, price_cl, price_net, price_pct_cl, vol_abs_cl, vol_pct_cl )

            x += 1
        logging.info('%s - populated new DF0 dataset' % cmi_debug )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)
                        # sucess = lobal class accessor (y_toplosers.df0) populated & updated
