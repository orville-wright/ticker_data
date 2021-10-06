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

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class screener_dg1:
    """Class to extract precanned screener data from finance.yahoo.com"""
    """https://finance.yahoo.com/screener/predefined/day_gainers"""
    """SCreener filter is: """
    """ 1. Percent Change:greater than 3 """
    """ 2. Region: United States """
    """ 3. Market Cap (Intraday): Mid Cap and Large Cap and Mega Cap """
    """ 4. Volume (Intraday):greater than 15000 """

    # global accessors
    dg1_df0 = ""          # DataFrame - Full list of top gainers
    dg1_df1 = ""          # DataFrame - Ephemerial list of top 10 gainers. Allways overwritten
    dg1_df2 = ""          # DataFrame - Top 10 ever 10 secs for 60 secs
    all_tag_tr = ""      # BS4 handle of the <tr> extracted data
    yti = 0
    cycle = 0           # class thread loop counter

    # TODO: top 10 loosers - no methods coded yet

    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INSTANTIATE' % cmi_debug )
        # init empty DataFrame with present colum names
        self.dg1_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.dg1_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.dg1_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.yti = yti
        return

# method #1
    def get_data(self):
        """Connect to finance.yahoo.com and extract (scrape) the raw sring data out of"""
        """the embedded/precanned webpage screener html data table. Returns a BS4 handle."""

        cmi_debug = __name__+"::"+self.get_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        r = requests.get("https://finance.yahoo.com/screener/predefined/small_cap_gainers" )
        logging.info('%s - read html stream' % cmi_debug )
        self.soup = BeautifulSoup(r.text, 'html.parser')
        # ATTR style search. Results -> Dict
        # <tr> tag has a very complex 'class=' but attributes are unique. e.g. 'simpTblRow'
        logging.info('%s store url data handle' % cmi_debug )
        self.all_tag_tr = self.soup.find_all(attrs={"class": "simpTblRow"})

        # Example CSS Selector
        #all_tag_tr1 = soup.select( "tr.simpTblRow.Bgc" )
        logging.info('%s close url handle' % cmi_debug )
        r.close()
        return

# method #2
    def build_df0(self):
        """Build-out Pandas DataFrame containg all the"""
        """extracted/scraped fields from the html/markup table data"""
        """Wrangle, clean/convert/format the data correctly."""

        cmi_debug = __name__+"::"+self.build_df0.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop all rows from DF0' % cmi_debug )
        self.dg1_df0.drop(self.dg1_df0.index, inplace=True)

        x = 1                               # row counter leveraged for unique dataframe key
        for datarow in self.all_tag_tr:                  # BS4 generator object (nice, but has BS4 accessiblity limits)
            extr_strs = datarow.strings
            co_sym = next(extr_strs)         # 1st <td> : ticker symbol info / e.g "NWAU"
            co_name = next(extr_strs)        # 2nd <td> : company name / e.g "Consumer Automotive Finance, Inc."
            price = next(extr_strs)          # 3rd <td> : price (Intraday) / e.g "0.0031"
            #logging.info( f'%s - >> 20 DEBUG<< Symbol: {co_sym} / price orig: {price} type: {type(price)}' % cmi_debug )
            # change_sign = next(extr_strs)    # DEPRECATED by Yahoo.com / 4.0-th <td> : $ change / e.g  "+0.0021"
            change_val = next(extr_strs)     # 4-th <td> : $ change / e.g  "+0.0021"
            #logging.info( f'%s - >> 30 DEBUG<< Symbol: {co_sym} / change_sign orig: {change_sign} type: {type(change_sign)}' % cmi_debug )
            #logging.info( f'%s - >> 31 DEBUG<< Symbol: {co_sym} / change_val orig: {change_val} type: {type(change_val)}' % cmi_debug )
            # pct_sign = next(extr_strs)     # DEPRECATED by Yahoo.com / 5.0-th <td> : % change / e.g "+" or "-"
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

            change_cl = re.sub('\%+-'', '', change_val)
            change_clean = np.float(change_cl)

            TRILLIONS = re.search('T', mktcap)
            BILLIONS = re.search('B', mktcap)
            MILLIONS = re.search('M', mktcap)

            if TRILLIONS:
                mktcap_clean = np.float(re.sub('T', '', mktcap))
                mb = "ST"
                logging.info('%s - Small Cap/TRILLIONS. set ST' % cmi_debug )

            if BILLIONS:
                mktcap_clean = np.float(re.sub('B', '', mktcap))
                mb = "SB"
                logging.info('%s - Small cap/BILLIONS. set SB' % cmi_debug )

            if MILLIONS:
                mktcap_clean = np.float(re.sub('M', '', mktcap))
                mb = "SM"
                logging.info('%s - Large cap/MILLIONS. set SM' % cmi_debug )

            if not TRILLIONS and not BILLIONS and not MILLIONS:
                mktcap_clean = 0    # error condition - possible bad data
                mb = "SZ"           # Zillions
                logging.info('%s - bad mktcap data N/A setting to SZ' % cmi_debug )
                # handle bad data in mktcap html page field

            if pct_val == "N/A":
                pct_val = float(0.0)        # Bad data. FOund a filed with N/A instead of read num
            else:
                pct_clean = re.sub('[\%+-]', "", pct_val )
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
            self.dg1_df0 = self.dg1_df0.append(self.df0)    # append this ROW of data into the REAL DataFrame
            x+=1
        logging.info('%s - populated new DF0 dataset' % cmi_debug )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)
                        # sucess = lobal class accessor (y_topgainers.*_df0) populated & updated

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
    def listall(self):
        """Print the full DataFrame table list of precanned screener: DAY GAINERS"""
        """Sorted by % Change"""
        # stock_topgainers = get_topgainers()
        cmi_debug = __name__+"::"+self.listall.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.dg1_df0.sort_values(by='Row', ascending=True ) )
        return

# method #5
    def build_top10(self):
        """Get top 10 enteries from main DF (df0) -> temp DF (df1)"""
        """df1 is ephemerial. Is allways overwritten on each run"""

        cmi_debug = __name__+"::"+self.build_top10.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        logging.info('%s - Drop all rows from DF1' % cmi_debug )
        self.dg1_df1.drop(self.dg1_df1.index, inplace=True)
        logging.info('%s - Copy DF0 -> ephemerial DF1' % cmi_debug )
        self.dg1_df1 = self.dg1_df0.sort_values(by='Pct_change', ascending=False ).copy(deep=True)    # create new DF via copy of top 10 entries
        self.dg1_df1.rename(columns = {'Row':'ERank'}, inplace = True)    # Rank is more accurate for this Ephemerial DF
        self.dg1_df1.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        return

# method #7
    def print_top10(self):
        """Prints the Top 20 Dataframe"""

        cmi_debug = __name__+"::"+self.print_top10.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.dg1_df1.sort_values(by='Pct_change', ascending=False ) )
        return

# method #6
    def build_10ten60(self, cycle):
        """Build-up 10x10x060 historical DataFrame (df2) from source df1"""
        """Generally called on some kind of cycle"""

        cmi_debug = __name__+"::"+self.build_10ten60.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        self.dg1_df2 = self.dg1_df2.append(self.dg1_df1, ignore_index=False)    # merge top 10 into
        self.dg1_df2.reset_index(inplace=True, drop=True)    # ensure index is allways unique + sequential
        return

# method #8
    def screener_logic(self):
        """Exectract a list of small cap **GAINERS ONLY** logic"""
        """ 1. Sort by Cur_price """
        """ 2. exclude any company with Market Cap < $299M """
        """ 3. manage company's with Market cap in BILLION's (requires special handeling) """
        """ 3. exclude any comany with %gain less than 5% """
        """ 4. SMALL CAP stocks only - Excludes Medium. Large, Mega cap companies!!"""

        cmi_debug = __name__+"::"+self.screener_logic.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)

        self.dg1_df1 = self.dg1_df0[self.dg1_df0.Mkt_cap > 299 ]       # limit to greater than $299M
        self.dg1_df1 =  pd.concat( [ self.dg1_df1, self.dg1_df0[self.dg1_df0.M_B == "SB"] ] )  # now capture all BILLIONS
        self.dg1_df1 = self.dg1_df1.sort_values(by=['Pct_change'], ascending=False )
        self.dg1_df1.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential

        # save some key stats items
        rx = {}
        ulp = self.dg1_df1['Cur_price'].min()
        lowestprice = self.dg1_df1['Cur_price'].min()
        minv = self.dg1_df1['Cur_price'].idxmin()
        lowsym = self.dg1_df1.loc[minv, ['Symbol']][0]
        lowconame = self.dg1_df1.loc[minv, ['Co_name']][0]

        # Allways make sure this is key #1 in the recommendations dict
        rx['1'] = ('Small cap % gainer:', lowsym.rstrip(), '$'+str(ulp), lowconame.rstrip(), '+%'+str(self.dg1_df1.loc[minv, ['Pct_change']][0]) )

        print ( f">>Lowest<< price OPPTY is: #{minv} - {lowconame.rstrip()} ({lowsym.rstrip()}) @ ${lowestprice}" )
        print ( " " )
        print ( self.dg1_df1 )
        return rx       # dict{}
