#! /home/orville/venv/devel/bin/python3
from requests_html import HTMLSession
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
import json
from rich import print

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################
# CLASS
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

#####################################################
# INIT
    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
        # init empty DataFrame with preset colum names
        self.args = global_args                                # Only set once per INIT. all methods are set globally
        self.up_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', "Vol", 'Vol_pct', 'Time' ] )
        self.down_df1 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', "Vol", 'Vol_pct', 'Time' ] )
        self.df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', "Vol", 'Vol_pct', 'Time' ] )
        self.yti = yti
        self.js_session = HTMLSession()                        # init JAVAScript processor early
        self.js_session.cookies.update(self.nasdaq_headers)    # load cookie/header hack data set into session
        return

#####################################################
# method #1
    def get_un_vol_data(self):
        """
        Access NEW nasdaq.com JAVASCRIPT page [unusual volume] and extract the native JSON dataset
        JSON dataset contains *BOTH* UP vol & DOWN vol for top 25 symbols, right now
        NO BeautifulSOup scraping needed anymore. We access the pure JSON datset via native API rest call
        note: Javascript engine is required, Cant process/read a JS page via requests(). The get() hangs forever
        """

        cmi_debug = __name__+"::"+self.get_un_vol_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        # Initial blind get
        # present ourself to NASDAQ.com so we can extract the critical cookie -> ak_bmsc
        # be nice and set a healthy cookie package
        logging.info('%s - blind get()' % cmi_debug )
        self.js_session.cookies.update(self.nasdaq_headers)    # redundent as it's done in INIT but I'm not sure its persisting from there
        with self.js_session.get("https://www.nasdaq.com", stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - EXTRACT/INSERT valid cookie  ' % cmi_debug )
                        #self.js_session.cookies.update({'ak_bmsc': self.js_resp0.cookies['ak_bmsc']} )    # NASDAQ cookie hack
            #self.js_session.cookies.update({'bm_sv': self.js_resp0.cookies['bm_sv']} )    # NASDAQ cookie hack

        # 2nd get with the secret nasdaq.com cookie no inserted
        logging.info('%s - rest API read json' % cmi_debug )
        with self.js_session.get("https://api.nasdaq.com/api/quote/list-type/unusual_volume", stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp2:
            logging.info('%s - json data extracted' % cmi_debug )
            logging.info('%s - store FULL json dataset' % cmi_debug )
            self.uvol_all_data = json.loads(self.js_resp2.text)
            logging.info('%s - store UP data locale' % cmi_debug )
            self.uvol_up_data =  self.uvol_all_data['data']['up']['table']['rows']
            logging.info('%s - store DOWN data locale' % cmi_debug )
            self.uvol_down_data = self.uvol_all_data['data']['down']['table']['rows']

        # DEBUG
        if self.args['bool_xray'] is True:
            print ( f"=xray=========================== {self.yti} ================================begin=" )
            print ( f"=== session cookies ===" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"=xray=========================== {self.yti} ==================================end=" )
        return

#####################################################
# method #2
# New method to build a Pandas DataFrame from JSON data structure
    def build_df(self, ud):
        """
        Build-out a fully populated DF containg the fields if interest from the JSON dataset.
        Wrangle, clean/convert/format & process the dirty data
        NOTE:  args: ud  (0 = get up volume  / 1 = get down volume)
        """

        #this_df = ""
        cmi_debug = __name__+"::"+self.build_df.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        if ud == 0:
            logging.info('%s - build UP df' % cmi_debug )
            self.up_df0 = pd.DataFrame()             # new df, but is NULLed
            this_df = self.up_df0
            dataset = self.uvol_up_data
        elif ud == 1:
            logging.info('%s - build DOWN df' % cmi_debug )
            self.down_df1 = pd.DataFrame()           # new df, but is NULLed
            this_df = self.down_df1
            dataset = self.uvol_down_data
        else:
            logging.info('%s - Error: invalid dataframe. EXITING' % cmi_debug )
            return 0

        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop all rows from DF' % cmi_debug )
        this_df.drop(this_df.index, inplace=True)
        x = 1    # row counter Also leveraged for unique dataframe key
        for json_data_row in dataset:
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
            # Row           = x              x
            # Symbol        = co_sym         co_sym_lj
            # Co_name       = co_name        co_name_lj
            # Cur_price     = price          price_cl
            # Prc_change    = price_net      price_net_cl
            # Pct_change    = price_pct      price_pct_cl
            # vol           = vol_abs        vol_abs_cl
            # vol_pct       = vol_pct        vol_pct_cl
            # Time          = time_now       time_now

            # wrangle, clean, cast & prepare the data
            co_sym_lj = np.array2string(np.char.ljust(co_sym, 6) )         # left justify TXT in DF & convert to raw string
            co_name_lj = (re.sub('[\'\"]', '', co_name) )                  # remove " ' and strip leading/trailing spaces
            co_name_lj = np.array2string(np.char.ljust(co_name_lj, 60) )   # left justify TXT in DF & convert to raw string
            co_name_lj = (re.sub('[\']', '', co_name_lj) )                 # remove " ' and strip leading/trailing spaces

            price_cl = (re.sub('[ $,]', '', price))                        # remove $ sign
            price_net_cl = (re.sub('[\-+]', '', price_net))                # remove - + signs
            price_pct_cl = (re.sub('[\-+%]', '', price_pct))               # remove - + % signs
            vol_abs_cl = (re.sub('[,]', '', vol_abs))                      # remove ,
            vol_pct_cl = (re.sub('[%]', '', vol_pct))                      # remover %

            self.list_data = [[ \
                       x, \
                       re.sub('\'', '', co_sym_lj), \
                       co_name_lj, \
                       round(float(price_cl), 2), \
                       round(float(price_net_cl), 2), \
                       round(float(price_pct_cl), 2), \
                       round(float(vol_abs_cl)), \
                       round(float(vol_pct_cl), 1), \
                       time_now ]]


            self.df_1_row = pd.DataFrame(self.list_data, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', "Vol", 'Vol_pct', 'Time' ], index=[x] )
            if ud == 0:
                logging.info( '%s - append UP Volume data into DataFrame' % cmi_debug )
                self.up_df0 = pd.concat([self.up_df0, self.df_1_row])    # append this ROW of data into the REAL DataFrame
            else:
                logging.info('%s - append DOWN Volume data into DataFrame' % cmi_debug )
                self.down_df1 = pd.concat([self.down_df1, self.df_1_row])    # append this ROW of data into the REAL DataFrame

            x += 1

        if ud == 0: self.up_df0.reset_index(inplace=True, drop=True)           # reset index each time so its guaranteed sequential
        if ud == 1: self.down_df1.reset_index(inplace=True, drop=True)         # reset index each time so its guaranteed sequential
        logging.info('%s - populated new DF' % cmi_debug )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)
                        # sucess = lobal class accessor (y_toplosers.df0) populated & updated

#####################################################
# method #3
    def up_unvol_listall(self):
        """
        Prepare a list from this NASDAQ unusual UP volume stocks DF.
        NOTE: This will sort by % Change & rest the index to match the new sort order.
              but will return a temp DF (list_up). Not the orignal DF up_df0
        """
        logging.info('ins.#%s.up_unvol_listall() - IN' % self.yti )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        list_up = self.up_df0.sort_values(by='Pct_change', ascending=False )
        list_up.reset_index(inplace=True, drop=True)           # reset index each time so its guaranteed sequential
        logging.info('ins.#%s.up_unvol_listall() - DONE' % self.yti )
        return list_up

#####################################################
# method #4
    def down_unvol_listall(self):
        """Print the full DataFrame table list of NASDAQ unusual DOWN volumes"""
        """Sorted by % Change"""
        logging.info('ins.#%s.down_unvol_listall() - IN' % self.yti )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        list_down = self.down_df1.sort_values(by='Pct_change', ascending=False )
        list_down.reset_index(inplace=True, drop=True)           # reset index each time so its guaranteed sequential
        logging.info('ins.#%s.down_unvol_listall() - DONE' % self.yti )
        return list_down

# method 5
    def up_down_combo(self):
        """Build a combo dataframe that hows all the reallnice results of UP and DOwn"""
        """UNusual volume data. Tag each row is an easy UP/DOWN tag"""
        logging.info('ins.#%s.up_down_combo() - IN' % self.yti )
        # should drop entire df before starting to ensure its empty
        self.df2=self.up_df0.copy()
        self.df2.drop('Row', axis=1, inplace=True )
        logging.info('ins.#%s.up_down_combo() - DONE' % self.yti )
        print ( f"{self.df2}" )
        return
