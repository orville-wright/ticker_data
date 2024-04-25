#!/usr/bin/python3
#import urllib
#import urllib.request
import requests

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
import threading
import types
import inspect

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class y_toplosers:
    """Class to extract Top Losers data set from finance.yahoo.com"""

    # global accessors
    tg_df0 = ""          # DataFrame - Full list of top loserers
    tg_df1 = ""          # DataFrame - Ephemerial list of top 10 loserers. Allways overwritten
    tg_df2 = ""          # DataFrame - Top 10 ever 10 secs for 60 secs
    all_tag_tr = ""      # BS4 handle of the <tr> extracted data
    yti = 0
    cycle = 0           # class thread loop counter

    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INSTANTIATE' % cmi_debug )
        # init empty DataFrame with present colum names
        self.tg_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.tg_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' 'Mkt_cap', 'M_B', 'Time'] )
        self.tg_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' 'Mkt_cap', 'M_B', 'Time'] )
        self.yti = yti
        return

# method #1
    def get_topg_data(self):
        """Connect to finance.yahoo.com and extract (scrape) the raw sring data out of"""
        """the embedded webpage [Stock:Top loserers] html data table. Returns a BS4 handle."""

        cmi_debug = __name__+"::"+self.get_topg_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        r = requests.get("https://finance.yahoo.com/losers" )
        logging.info('%s - read html stream' % cmi_debug )
        self.soup = BeautifulSoup(r.text, 'html.parser')

        # ATTR style search. Results -> Dict
        # <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
        logging.info('%s - save data handle' % cmi_debug )
        self.all_tag_tr = self.soup.find_all(attrs={"class": "simpTblRow"})

        # target markup line I am scanning looks like this...
        # soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc($extraLightBlue)" )
        # Example CSS Selector
        #all_tag_tr1 = soup.select( "tr.simpTblRow.Bgc" )

        logging.info('%s - close url handle' % cmi_debug )
        return

# method #2
    def build_tg_df0(self):
        """Build-out a fully populated Pandas DataFrame containg all the"""
        """extracted/scraped fields from the html/markup table data"""
        """Wrangle, clean/convert/format the data correctly."""

        cmi_debug = __name__+"::"+self.build_tg_df0.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop all rows from DF0' % cmi_debug )
        #self.tg_df0.drop(self.tg_df0.index, inplace=True)           # the df is now 100% empty
        self.tg_df0 = pd.DataFrame()                                 # new df, but is NULLed. avoids empty concat errors
        x = 1    # row counter Also leveraged for unique dataframe key
        for datarow in self.all_tag_tr:
            # 1st <td> cell : ticker symbol info & has comment of company name
            # 2nd <td> cell : company name
            # 3rd <td> cell : price
            # 4th <td> cell : $ change
            # 5th <td> cell : % change
            # more cells in <tr> data row...but I'm not interested in them at moment.

            # BS4 generator object comes from "extracted strings" BS4 operation (nice)
            extr_strings = datarow.stripped_strings
            co_sym = next(extr_strings)
            co_name = next(extr_strings)
            price = next(extr_strings)
            change = next(extr_strings)
            pct = next(extr_strings)
            vol = next(extr_strings)
            avg_vol = next(extr_strings)
            mktcap = next(extr_strings)

            co_sym_lj = np.array2string(np.char.ljust(co_sym, 6) )      # left justify TXT in DF & convert to raw string

            co_name_lj = (re.sub('[\'\"]', '', co_name) )    # remove " ' and strip leading/trailing spaces
            co_name_lj = np.array2string(np.char.ljust(co_name_lj, 25) )   # left justify TXT in DF & convert to raw string
            co_name_lj = (re.sub('[\']', '', co_name_lj) )    # remove " ' and strip leading/trailing spaces

            TRILLIONS = re.search('T', mktcap)
            BILLIONS = re.search('B', mktcap)
            MILLIONS = re.search('M', mktcap)

            if TRILLIONS:
                mktcap_clean = float(re.sub('T', '', mktcap))
                mb = "T"
                logging.info('%s - found TRILLIONS. set T' % cmi_debug )

            if BILLIONS:
                mktcap_clean = float(re.sub('B', '', mktcap))
                mb = "B"
                logging.info('%s - found BILLIONS. set B' % cmi_debug )

            if MILLIONS:
                mktcap_clean = float(re.sub('M', '', mktcap))
                mb = "M"
                logging.info('%s - found MILLIONS. set M' % cmi_debug )

            if not TRILLIONS and not BILLIONS and not MILLIONS:
                mktcap_clean = 0    # error condition - possible bad data
                mb = "Z"            # Zillions !!
                logging.info('%s - found TRILLIONS. set T' % cmi_debug )
                # handle bad data in mktcap html page field

            if pct == "N/A":            # Bad data. FOund a filed with N/A instead of read num
                pct = "1.0"

            pct = float(re.sub('[\-+,%]', '', pct))
            change = float(re.sub('[\-+,%]', '', change))
            #float(re.sub('[\+,]', '', change)), \

            # note: Pandas DataFrame : top_loserers pre-initalized as EMPTY
            # Data treatment:
            # Data is extracted as raw strings, so needs wrangeling...
            #    price - stip out any thousand "," seperators and cast as true decimal via numpy
            #    change - strip out chars '+' and ',' and cast as true decimal via numpy
            #    pct - strip out chars '+ and %' and cast as true decimal via numpy
            #    mktcap - strio out 'B' Billions & 'M' Millions
                       #float(re.sub('\,', '', price)), \
            self.list_data = [[ \
                       x, \
                       re.sub('\'', '', co_sym_lj), \
                       co_name_lj, \
                       price, \
                       change, \
                       pct, \
                       mktcap_clean, \
                       mb, \
                       time_now ]]

            #self.df0 = pd.DataFrame(self.data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time' ], index=[x] )
            #self.tg_df0 = self.tg_df0._append(self.df0)    # append this ROW of data into the REAL DataFrame
            # convert our list into a 1 row dataframe
            self.df_1_row = pd.DataFrame(self.list_data, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time' ], index=[x] )
            self.tg_df0 = pd.concat([self.tg_df0, self.df_1_row])  
            x+=1

        logging.info('%s - populated new DF0 dataset' % cmi_debug )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)
                        # sucess = lobal class accessor (y_toplosers.tg_df0) populated & updated

# method #3
# Hacking function - keep me arround for a while
    def prog_bar(self, x, y):
        """simple progress dialogue function"""
        if x % y == 0:
            print ( " " )
        else:
            print ( ".", end="" )
        return

# method #4
    def topg_listall(self):
        """Print the full DataFrame table list of Yahoo Finance Top loserers"""
        """Sorted by % Change"""

        cmi_debug = __name__+"::"+self.topg_listall.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.tg_df0.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built
        return

# method #5
    def build_top10(self):
        """Get top 10 loserers from main DF (df0) -> temp DF (df1)"""
        """df1 is ephemerial. Is allways overwritten on each run"""

        cmi_debug = __name__+"::"+self.build_top10.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        logging.info('%s - Drop all rows from DF1' % cmi_debug )
        self.tg_df1.drop(self.tg_df1.index, inplace=True)
        logging.info('%s - Copy DF0 -> ephemerial DF1' % cmi_debug )
        #self.tg_df1 = self.tg_df0.sort_values(by='Pct_change', ascending=False ).copy(deep=True)    # create new DF via copy of top 10 entries
        self.tg_df1 = self.tg_df0.sort_values(by='Pct_change', ascending=False ).head(20).copy(deep=True)    # create new DF via copy of top 10 entries
        self.tg_df1.rename(columns = {'Row':'ERank'}, inplace = True)   # Rank is more accurate for this Ephemerial DF
        self.tg_df1.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        return

# method #7
    def print_top10(self):
        """Prints the Top 10 Dataframe"""

        cmi_debug = __name__+"::"+self.print_top10.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.tg_df1.sort_values(by='Pct_change', ascending=False ).head(20) )
        return

# method #6
    def build_tenten60(self, cycle):
        """Build-up 10x10x060 historical DataFrame (df2) from source df1"""
        """Generally called on some kind of cycle"""

        cmi_debug = __name__+"::"+self.build_tenten60.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        self.tg_df2 = self.tg_df2.append(self.tg_df1, ignore_index=False)    # merge top 10 into
        self.tg_df2.reset_index(inplace=True, drop=True)    # ensure index is allways unique + sequential
        return
