#!/usr/bin/python3
import urllib
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
import threading

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class unusual_vol:
    """Class to discover unusual volume data from NASDAQ.com data source"""

    # global accessors
    up_df0 = ""                # DataFrame - Full list of Unusual UP volume
    down_df1 = ""                # DataFrame - Full list of Unusual DOWN volume
    df2 = ""                # DataFrame - List of Top 10 (both UP & DOWN
    up_table_data = ""      # BS4 constructor object of HTML <table> sub-doc > UP vol data
    down_table_data = ""    # BS4 constructor object of HTML <table> sub-doc > DOWN vol data
    yti = 0                 # Unique instance identifier
    cycle = 0               # class thread loop counter
    soup = ""               # BS4 shared handle between UP & DOWN (1 URL, 2 embeded data sets in HTML doc)
    args = []               # class dict to hold global args being passed in from main() methods

    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INSTANTIATE' % cmi_debug )
        self.args = global_args
        # init empty DataFrame with preset colum names
        self.up_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Vol', 'Vol_pct', 'Time'] )
        self.down_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Vol', 'Vol_pct', 'Time'] )
        self.df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Vol', 'Vol_pct', 'Time'] )
        self.yti = yti
        return

# method #1
    def get_up_unvol_data(self):
        """Connect to old.nasdaq.com and extract (scrape) the raw HTML string data from"""
        """the embedded html data table [UP_on_unusual_vol ]. Returns a BS4 handle."""

        cmi_debug = __name__+"::"+self.get_up_unvol_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        with urllib.request.urlopen("https://old.nasdaq.com/markets/unusual-volume.aspx") as url:
            s = url.read()
            logging.info('%s - read html stream' % cmi_debug )
            self.soup = BeautifulSoup(s, "html.parser")

        logging.info('%s - save BS4 class data object' % cmi_debug )
        self.all_tagid_up = self.soup.find( id="_up" )           # locate the section with ID = '_up' > output RAW htnml
        self.up_table_data = self.all_tagid_up.table             # move into the <table> section > ouput RAW HTML
        self.up_table_rows = ( tr_row for tr_row in ( self.up_table_data.find_all( 'tr' ) ) )      # build a generattor of <tr> objects

        # other HTML accessor methods - good for reference
        #self.up_table_rows = self.up_table_data.find_all( "tr")
        #self.up_table_rows = self.up_table_data.tr
        #self.up_table_rows2 = self.up_table_data.td

        logging.info('%s - close url handle' % cmi_debug )
        url.close()
        return

# method #2
    def get_down_unvol_data(self):
        """Connect to old.nasdaq.com and extract (scrape) the raw HTML string data from"""
        """the embedded html data table [DOWN_on_unusual_vol ]. Returns a BS4 handle."""

        cmi_debug = __name__+"::"+self.get_down_unvol_data.__name__+".#"+str(self.yti)
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
