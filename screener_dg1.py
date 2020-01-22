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

        logging.info('ins.#%s.get_data() - IN' % self.yti )
        with urllib.request.urlopen("https://finance.yahoo.com/screener/predefined/small_cap_gainers" ) as url:
            s = url.read()
            logging.info('ins.#%s.get_data() - read html stream' % self.yti )
            self.soup = BeautifulSoup(s, "html.parser")
        # ATTR style search. Results -> Dict
        # <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
        logging.info('ins.#%s.get_data() - save data handle' % self.yti )
        self.all_tag_tr = self.soup.find_all(attrs={"class": "simpTblRow"})

        # target markup line I am scanning looks like this...
        # soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc($extraLightBlue)" )

        # Example CSS Selector
        #all_tag_tr1 = soup.select( "tr.simpTblRow.Bgc" )
        logging.info('ins.#%s.get_data() - close url handle' % self.yti )
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
        self.dg1_df0.drop(self.dg1_df0.index, inplace=True)
        x = 1    # row counter Also leveraged for unique dataframe key
        for datarow in self.all_tag_tr:
            # 1st <td> : ticker symbol info & has comment of company name
            # 2nd <td> : company name
            # 3rd <td> : price
            # 4th <td> : $ change
            # 5th <td> : % change
            # 6th <td> : volume
            # 6th <td> : Avg. vol over 3 months)
            # 7th <td> : Market cap
            # 8th <td> : PE ratio

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

            co_sym_lj = np.char.ljust(co_sym, 6)       # use numpy to left justify TXT in pandas DF
            co_name_lj = np.char.ljust(co_name, 20)    # use numpy to left justify TXT in pandas DF
            mktcap = (re.sub('[N\/A]', '0', mktcap))   # handle N/A

            BILLIONS = re.search('B', mktcap)
            MILLIONS = re.search('M', mktcap)
            if BILLIONS:
                mktcap_clean = np.float(re.sub('B', '', mktcap))
                mb = "B"

            if MILLIONS:
                mktcap_clean = np.float(re.sub('M', '', mktcap))
                mb = "M"

            # note: Pandas DataFrame : top_gainers pre-initalized as EMPYT
            # Data treatment:
            # Data is extracted as raw strings, so needs wrangeling...
            #    price - stip out any thousand "," seperators and cast as true decimal via numpy
            #    change - strip out chars '+' and ',' and cast as true decimal via numpy
            #    pct - strip out chars '+ and %' and cast as true decimal via numpy
            #    mktcap - strio out 'B' Billions & 'M' Millions & "N/A"
            self.data0 = [[ \
                       x, \
                       co_sym_lj, \
                       co_name_lj, \
                       np.float(re.sub('\,', '', price)), \
                       np.float(re.sub('[\+,]', '', change)), \
                       np.float(re.sub('[\+%]', '', pct)), \
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
        #print ( self.dg1_df0.sort_values(by='Pct_change', ascending=False ) )
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
        self.dg1_df1 = self.dg1_df0.sort_values(by='Pct_change', ascending=False ).head(10).copy(deep=True)    # create new DF via copy of top 10 entries
        self.dg1_df1.rename(columns = {'Row':'ERank'}, inplace = True)    # Rank is more accurate for this Ephemerial DF
        self.dg1_df1.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        return

# method #7
    def print_top10(self):
        """Prints the Top 10 Dataframe"""

        cmi_debug = __name__+"::"+self.print_top10.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.dg1_df1.sort_values(by='Pct_change', ascending=False ).head(10) )
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
    def screen_logic(self):
        """Exectracts a list based on my personla screening logic"""
        """ 1. Sort by Cur_price """
        """ 2. exclude any company with Market Cap < $750M """
        """ 3. manage company's with Market cap in BILLION's (requires special handeling) """
        """ 3. exclude any comany with %gain less than 5% """

        cmi_debug = __name__+"::"+self.screen_logic.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        self.dg1_df1 = self.dg1_df0.query('Mkt_cap > 750.000' ).copy(deep=True)       # capture MILLIONS 1st
        self.dg1_df1 =  pd.concat([self.dg1_df1, self.dg1_df0.query('M_B == "B"')] )  # now capture BILLIONS & concat both results
        self.dg1_df1 = self.dg1_df1.sort_values(by=['Cur_price'], ascending=False )
        self.dg1_df1.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        print ( self.dg1_df1 )
        return
