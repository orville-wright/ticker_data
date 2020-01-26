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
    """Class to discover and extract unusual volume data from NASDAQ.com data source"""

    # global accessors
    df0 = ""                # DataFrame - Full list of top gainers
    df1 = ""                # DataFrame - Ephemerial list of top 10 gainers. Allways overwritten
    df2 = ""                # DataFrame - Top 10 ever 10 secs for 60 secs
    up_table_data = ""      # BS4 handle of the <table> with UP vol data
    down_table_data = ""    # BS4 handle of the <table> with UP vol data
    yti = 0                 # Unique instance identifier
    cycle = 0               # class thread loop counter

    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INSTANTIATE' % cmi_debug )
        #logging.info('y_toplosers:: Inst #: %s' % yti )    # catches 1st instantiate 0|1
        # init empty DataFrame with present colum names
        self.tg_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', "Vol", 'Vol_pct', 'Time'] )
        self.tg_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' "Vol", 'Vol_pct', 'Time'] )
        self.tg_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' "Vol", 'Vol_pct', 'Time'] )
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
        # ATTR style search. Results -> Dict
        # <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
        logging.info('%s - save data handle' % cmi_debug )
        self.all_tagid_up = self.soup.find( id="_up" )           # locate the section ID'd: '_up'
        self.up_table_data = self.all_tagid_up.table       # move into the <table> section

        logging.info('%s - close url handle' % cmi_debug )
        url.close()
        return

# method #2
    def build_df0(self):
        """Build-out a fully populated Pandas DataFrame containg all the"""
        """extracted/scraped fields from the html/markup table data"""
        """Wrangle, clean/convert/format the data correctly."""

        cmi_debug = __name__+"::"+self.build_df0.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop all rows from DF0' % cmi_debug )
        #self.build_df0.drop(self.build_df0.index, inplace=True)

        x = 1    # row counter Also leveraged for unique dataframe key
        for datarow in self.up_table_data.find_all( "tr" )[1:]:    # skip the first <tr> = column names
            extr_strings = datarow.stripped_strings
            # this is sloppy. It doesn't precisely examine the 7 <td> cells with each <tr>
            # it just grabs all the TEXT tstring it can find
            co_sym = next(extr_strings)
            co_name = next(extr_strings)
            price = next(extr_strings)
            change_blob = next(extr_strings)
            vol_abs = next(extr_strings)
            vol_pct = next(extr_strings)

            co_sym_lj = np.char.ljust(co_sym, 6)       # use numpy to left justify TXT in pandas DF
            co_name_lj = np.char.ljust(co_name, 20)    # use numpy to left justify TXT in pandas DF

            price_cl = (re.sub('[ $]', '', price))
            vol_abs_cl = (re.sub('[\+ ,]', '', vol_abs))
            vol_pct_cl = (re.sub('[\+,% ]', '', vol_pct))
            change_blob_cl = (re.sub('[▲]', '', change_blob))  # remove special char symbol &#x00e2;&#x0096;&#x00b2;
            # note: Pandas DataFrame : top_loserers pre-initalized as EMPYT
            # Data treatment:
            # Data is extracted as raw strings, so needs wrangeling...
            #    price - stip out any thousand "," seperators and cast as true decimal via numpy
            #    change - strip out chars '+' and ',' and cast as true decimal via numpy
            #    pct - strip out chars '+ and %' and cast as true decimal via numpy
            #    mktcap - strio out 'B' Billions & 'M' Millions
            """
            self.data0 = [[ \
                       x, \
                       co_sym_lj, \
                       co_name_lj, \
                       np.float(re.sub('\,$', '', price)), \
                       np.float(re.sub('[\+,]', '', change)), \
                       np.float(re.sub('[\+,%]', '', pct)), \
                       mktcap_clean, \
                       time_now ]]

            self.df0 = pd.DataFrame(self.data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'Time' ], index=[x] )
            self.tg_df0 = self.tg_df0.append(self.df0)    # append this ROW of data into the REAL DataFrame
            """
            x+=1
            print ( co_sym, " ", co_name, " ", price_cl, " ", change_blob_cl, " ", vol_abs_cl, " ", vol_pct_cl )

        logging.info('%s - populated new DF0 dataset' % cmi_debug )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)
                        # sucess = lobal class accessor (y_toplosers.tg_df0) populated & updated

"""
print ( " " )
print ( "==================== UNUSUAL volume down ====================" )
tag_1b = soup.find( id="_down" )
tag_1c = tag_1b.table
x = 0
for datarow in tag_1c.find_all( "tr" )[1:]:    # skips the first <tr> which is table column names

    extr_strings = datarow.stripped_strings
    co_sym = next(extr_strings)
    co_name = next(extr_strings)
    price = next(extr_strings)
    change = next(extr_strings)
    pct = next(extr_strings)
    vol = next(extr_strings)

    print ( co_sym, " ", co_name, " ", price, " ", change, " ", pct, " ", vol )

    x+=1
    print ( "============================ ", x, " ===================================" )
"""
