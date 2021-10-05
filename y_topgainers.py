#!/usr/bin/python3
import requests
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

class y_topgainers:
    """Class to extract Top Gainer data set from finance.yahoo.com"""

    # global accessors
    tg_df0 = ""          # DataFrame - Full list of top gainers
    tg_df1 = ""          # DataFrame - Ephemerial list of top 10 gainers. Allways overwritten
    tg_df2 = ""          # DataFrame - Top 10 ever 10 secs for 60 secs
    all_tag_tr = ""      # BS4 handle of the <tr> extracted data
    yti = 0
    cycle = 0           # class thread loop counter

    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
        # init empty DataFrame with present colum names
        self.tg_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.tg_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.tg_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.yti = yti
        return

# method #1
    def get_topg_data(self):
        """Connect to finance.yahoo.com and extract (scrape) the raw sring data out of"""
        """the embedded webpage [Stock:Top Gainers] html data table. Returns a BS4 handle."""

        cmi_debug = __name__+"::"+self.get_topg_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        r = requests.get("https://finance.yahoo.com/gainers" )
        logging.info('%s - read html stream' % cmi_debug )
        self.soup = BeautifulSoup(r.text, 'html.parser')

        # ATTR style search. Results -> Dict
        # <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
        logging.info('%s - save data object handle' % cmi_debug )
        self.all_tag_tr = self.soup.find_all(attrs={"class": "simpTblRow"})   # simpTblRow
        logging.info('%s - close url handle' % cmi_debug )
        return


    def dump_all_tag_tr(self):
        print ( "Dumping ALL_TAG_TR..." )
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
        self.tg_df0.drop(self.tg_df0.index, inplace=True)
        x = 1    # row counter Also leveraged for unique dataframe key
        for datarow in self.all_tag_tr:                  # BS4 generator object (nice, but has BS4 accessiblity limits)
            extr_strs = datarow.strings
            co_sym = next(extr_strs)         # 1st <td> : ticker symbol info / e.g "NWAU"
            co_name = next(extr_strs)        # 2nd <td> : company name / e.g "Consumer Automotive Finance, Inc."
            price = next(extr_strs)          # 3rd <td> : price (Intraday) / e.g "0.0031"
            #logging.info( f'%s - >> 20 DEBUG<< Symbol: {co_sym} / price orig: {price} type: {type(price)}' % cmi_debug )
            change_sign = next(extr_strs)    # 4.0-th <td> : $ change / e.g  "+0.0021"
            change_val = next(extr_strs)     # 4.1-th <td> : $ change / e.g  "+0.0021"
            #logging.info( f'%s - >> 30 DEBUG<< Symbol: {co_sym} / change_sign orig: {change_sign} type: {type(change_sign)}' % cmi_debug )
            #logging.info( f'%s - >> 31 DEBUG<< Symbol: {co_sym} / change_val orig: {change_val} type: {type(change_val)}' % cmi_debug )
            pct_sign = next(extr_strs)       # 5.0-th <td> : % change / e.g "+" or "-"
            pct_val = next(extr_strs)        # 5.1-th <td> : % change / e.g "210.0000%" WARN trailing "%" must be removed before casting to float
            #logging.info( f'%s - >> 32 DEBUG<< Symbol: {co_sym} / pct_sign orig: {pct_sign} type: {type(pct_sign)}' % cmi_debug )
            vol = next(extr_strs)            # 6th <td> : volume with scale indicator/ e.g "70.250k"
            avg_vol = next(extr_strs)        # 6th <td> : Avg. vol over 3 months) / e.g "61,447"
            mktcap = next(extr_strs)         # 7th <td> : Market cap with scale indicator / e.g "15.753B"
            peratio = next(extr_strs)        # 8th <td> : PEsratio TTM (Trailing 12 months) / e.g "N/A"
            #mini_gfx = next(extr_strs)      # 9th <td> : IGNORED = mini-canvas graphic 52-week rnage current price range with scale (no TXT/strings avail)

            ####################################################################
            # now wrangle the data...

            co_sym_lj = np.array2string(np.char.ljust(co_sym, 6) )          # left justify TXT in DF & convert to raw string

            # TODO: look at using f-string justifers to do this
            co_name_lj = (re.sub('[\'\"]', '', co_name) )                   # remove " ' and strip leading/trailing spaces
            co_name_lj = np.array2string(np.char.ljust(co_name_lj, 25) )    # left justify TXT in DF & convert to raw string
            co_name_lj = (re.sub('[\']', '', co_name_lj) )                  # remove " ' and strip leading/trailing spaces
            price_clean = float(price)
            mktcap = (re.sub('[N\/A]', '0', mktcap))   # handle N/A
            change_clean = np.float(change_val)

            TRILLIONS = re.search('T', mktcap)
            BILLIONS = re.search('B', mktcap)
            MILLIONS = re.search('M', mktcap)

            if TRILLIONS:
                mktcap_clean = np.float(re.sub('T', '', mktcap))
                mb = "XT"
                logging.info('%s - Mega Cap/TRILLIONS. set XT' % cmi_debug )

            if BILLIONS:
                mktcap_clean = np.float(re.sub('B', '', mktcap))
                mb = "LB"
                logging.info('%s - Large cap/BILLIONS. set LB' % cmi_debug )

            if MILLIONS:
                mktcap_clean = np.float(re.sub('M', '', mktcap))
                mb = "LM"
                logging.info('%s - Large cap/MILLIONS. set LM' % cmi_debug )

            if not TRILLIONS and not BILLIONS and not MILLIONS:
                mktcap_clean = 0    # error condition - possible bad data
                mb = "LZ"           # Zillions
                logging.info('%s - bad mktcap data N/A setting to LZ' % cmi_debug )
                # handle bad data in mktcap html page field

            if pct_val == "N/A":
                pct_val = float(0.0)        # Bad data. FOund a filed with N/A instead of read num
            else:
                pct_clean = re.sub('[\%,]', "", pct_val )
                pct_clean = float(pct_clean)

            self.data0 = [[ \
                       x, \
                       re.sub('\'', '', co_sym_lj), \
                       co_name_lj, \
                       np.float(re.sub('\,', '', price)), \
                       change_clean, \
                       pct_clean, \
                       mktcap_clean, \
                       mb, \
                       time_now ]]

            self.df0 = pd.DataFrame(self.data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time' ], index=[x] )
            self.tg_df0 = self.tg_df0.append(self.df0)    # append this ROW of data into the REAL DataFrame
            x+=1
        logging.info('%s - populated new DF0 dataset' % cmi_debug )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)
                        # sucess = lobal class accessor (y_topgainers.tg_df0) populated & updated

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
        """Print the full DataFrame table list of Yahoo Finance Top Gainers"""
        """Sorted by % Change"""

        cmi_debug = __name__+"::"+self.topg_listall.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.tg_df0.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built
        return

# method #5
    def build_top10(self):
        """Get top 15 gainers from main DF (df0) -> temp DF (df1)"""
        """df1 is ephemerial. Is allways overwritten on each run"""

        cmi_debug = __name__+"::"+self.build_top10.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        logging.info('%s - Drop all rows from DF1' % cmi_debug )
        self.tg_df1.drop(self.tg_df1.index, inplace=True)
        logging.info('%s - Copy DF0 -> ephemerial DF1' % cmi_debug )
        self.tg_df1 = self.tg_df0.sort_values(by='Pct_change', ascending=False ).head(15).copy(deep=True)    # create new DF via copy of top 10 entries
        self.tg_df1.rename(columns = {'Row':'ERank'}, inplace = True)    # Rank is more accurate for this Ephemerial DF
        self.tg_df1.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        return

# method #7
    def print_top10(self):
        """Prints the Top 10 Dataframe"""

        cmi_debug = __name__+"::"+self.print_top10.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.tg_df1.sort_values(by='Pct_change', ascending=False ).head(15) )
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
