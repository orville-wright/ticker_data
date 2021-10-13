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
import json

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class y_techevents:
    """
    Class to extract Simple Today/Short/Medium/Long term indicator data set from finance.yahoo.com
    """

    # global accessors
    te_resp0 = ""
    te_jsondata0 = ""
    te_zone = ""
    te_short = ""
    te_mid = ""
    te_long = ""
    te_srs_zone = ""
    te_df0 = ""          # DataFrame - Full list of top gainers
    te_df1 = ""          # DataFrame - Ephemerial list of top 10 gainers. Allways overwritten
    te_df2 = ""          # DataFrame - Top 10 ever 10 secs for 60 secs
    te_all_url = ""
    yti = 0
    cycle = 0           # class thread loop counter

    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f"{cmi_debug} - Instantiate.#{yti}" )
        # init empty DataFrame with present colum names
        self.te_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.te_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.te_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.yti = yti
        return


# method #1
    def form_api_endpoints(self, symbol):
        """
        For Technical event Indicators endpoint for the req get()
        This page is where the Free view into some technical idicators are show with full TEXT strings descriptions.
        NOTE: This is a teaser page. Tech Events are only available to paid-for subscrption users. But the teaser page shows
        a clutch of free indicators...So we'll take the free Tech Event indicators, for now.
        1. Today, Short, intermediate, Long Term technical analysis
        2. Support, Resistance, Stop loss levels
        """
        cmi_debug = __name__+"::"+self.form_api_endpoints.__name__+".#"+str(self.yti)
        logging.info( f"{cmi_debug} - form API endpoint URL(s)" )
        self.symbol = symbol.upper()
        self.te_url = "https://finance.yahoo.com/chart/" + self.symbol + "?Technical="
        self.te_all_url = "https://finance.yahoo.com/quote/" + self.symbol + "?p=" + self.symbol
        self.te_short_url = "https://finance.yahoo.com/chart/" + self.symbol + "?Technical=short"
        self.te_mid_url = "https://finance.yahoo.com/chart/" + self.symbol + "?Technical=intermediate"
        self.te_long_url = "https://finance.yahoo.com/chart/" + self.symbol + "?Technical=long"
        #
        logging.info( f"================================ Tech Events API endpoints ================================" )
        logging.info( f"{cmi_debug} - API endpoint #0: [ {self.te_url} ]" )
        logging.info( f"{cmi_debug} - API endpoint #1: [ {self.te_all_url} ]" )
        logging.info( f"{cmi_debug} - API endpoint #1: [ {self.te_short_url} ]" )
        logging.info( f"{cmi_debug} - API endpoint #3: [ {self.te_mid_url} ]" )
        logging.info( f"{cmi_debug} - API endpoint #4: [ {self.te_long_url} ]" )
        return


# method #2
    def get_te_zones(self):
        """
        Connect to finance.yahoo.com and extract (scrape) the raw JSON data out of
        the embedded webpage [finance.yahoo.com/chart/GOL?technical=short] html data table.
        Sabe JSON to class global attribute: self.te_resp0.text
        """
        cmi_debug = __name__+"::"+self.get_te_zones.__name__+".#"+str(self.yti)
        logging.info( f"{cmi_debug} - IN" )
        with requests.get( self.te_all_url, stream=True, timeout=5 ) as self.te_resp0:
            logging.info( f"{cmi_debug} - get() data / storing..." )
            self.soup = BeautifulSoup(self.te_resp0.text, 'html.parser')
            logging.info( f"{cmi_debug} - Main data zone: {len(self.soup)} lines extracted / Done" )
            #print ( f">>>DEBUG<<< : te_zone :\n{self.soup}" )

            #self.te_jsondata0 = json.loads(self.te_resp0.text)
        #
        #self.te_zone = self.soup.find('tch-evnts' )
        #self.te_zone = self.soup.find(attrs={"data-test": "tch-evnts"} )
        self.te_zone = self.soup.find(attrs={"id": "chrt-evts-mod"} )
        self.te_lizones = self.te_zone.find_all('li')
        self.te_title = self.te_zone.find_all(attrs={"class": "IbBlock W(60%)"} )
        #self.te_azones= self.te_lizones.a
        # self.te_zone_title = self.te_lizones.find(attrs={"class": "IbBlock"} )
        #self.te_zone_i = self.soup.button.find_all()
        #self.te_zone_l = self.soup.find_all('button')
        print ( f"\n>>>DEBUG<<< : te_zone : {len(self.te_zone)}  \n{self.te_zone}" )
        # self.te_short = self.te_zone.find(attrs={"value": "short"} )
        # self.te_mid = self.te_zone.find(attrs={"value": "intermediate"} )
        # self.te_long = self.te_zone.find(attrs={"value": "long"} )
        # self.te_srs_zone = self.te_zone.find(attrs={"class": "D(ib) Va(m) Mstart(30px) Fz(s)"} )
        # self.te_srs_combo = self.te_srs_zone.strings
        return


# method #3
    def build_te_data(self):
        """
        Build-out a fully populated Pandas DataFrame containg all the extracted/scraped fields from the
        html/markup table data Wrangle, clean/convert/format the data correctly.
        """
        cmi_debug = __name__+"::"+self.build_te_data.__name__+".#"+str(self.yti)
        logging.info( f"{cmi_debug} - IN" )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info( f"{cmi_debug} - Drop all rows from DF0" )
        #self.tg_df0.drop(self.tg_df0.index, inplace=True)
        x = 0   # row counter / = index_id for DataFrame
        print ( f"===== <li> zones: {len(self.te_lizones)}  =================" )
        #for j in self.te_zone.find_all('button'):
        for j in self.te_lizones:
            # >>>DEBUG<< for when yahoo.com changes data model...
            y = 1
            for i in j:
                print ( f"Data {y}: {i}" )
                print ( f"Tech Event: {i.svg}" )
                # logging.info( f'%s - Data: {j.td.strings}' % cmi_debug )
                y += 1
            print ( f"==============================================" )

            """
            extr_strs = j.strings
            co_sym = next(extr_strs)             # 1 : ticker symbol info / e.g "NWAU"
            co_name = next(extr_strs)            # 2 : company name / e.g "Consumer Automotive Finance, Inc."
            price = next(extr_strs)              # 3 : price (Intraday) / e.g "0.0031"

            change_sign = next(extr_strs)        # 4 : $ change sign / e.g  "+0.0021"
            if change_sign == "+" or change_sign == "-":
                change_val = next(extr_strs)     # 5 : $ change / e.g  "+0.0021"
            else:
                change_val = change_sign
                logging.info( f"{cmi_debug} - {co_sym} / re-align extract head / no [+-] field for $0" )
            pct_sign = next(extr_strs)           # 6 : % change / e.g "+" or "-"
            if pct_sign == "+" or pct_sign == "-":
                pct_val = next(extr_strs)        # 7 : change / e.g "210.0000%" WARN trailing "%" must be removed before casting to float
            else:
                z = 0
                pct_val = pct_sign
                logging.info( f"{cmi_debug} - {co_sym} / re-align extract head / no [+-] field for %0" )

            vol = next(extr_strs)            # 8 : volume with scale indicator/ e.g "70.250k"
            avg_vol = next(extr_strs)        # 9 : Avg. vol over 3 months) / e.g "61,447"
            mktcap = next(extr_strs)         # 10 : Market cap with scale indicator / e.g "15.753B"
            peratio = next(extr_strs)        # 11 : PEsratio TTM (Trailing 12 months) / e.g "N/A"
            #mini_gfx = next(extr_strs)      # 12th : IGNORED = mini-canvas graphic 52-week rnage (no TXT/strings avail)

            ####################################################################
            # now wrangle the data...
            co_sym_lj = f"{co_sym:<6}"          # left justify TXT in DF & convert to raw string
            co_name_lj = np.array2string(np.char.ljust(co_name, 25) )    # left justify TXT in DF & convert to raw string
            co_name_lj = (re.sub('[\'\"]', '', co_name_lj) )                  # remove " ' and strip leading/trailing spaces
            price_clean = float(price)
            mktcap = (re.sub('[N\/A]', '0', mktcap))   # handle N/A
            change_clean = np.float(change_val)

            TRILLIONS = re.search('T', mktcap)
            BILLIONS = re.search('B', mktcap)
            MILLIONS = re.search('M', mktcap)

            if TRILLIONS:
                mktcap_clean = np.float(re.sub('T', '', mktcap))
                mb = "ST"
                logging.info( f'%s - {x} / {co_sym_lj} Small Cap/TRILLIONS. set ST' % cmi_debug )

            if BILLIONS:
                mktcap_clean = np.float(re.sub('B', '', mktcap))
                mb = "SB"
                logging.info( f'%s - {x} / {co_sym_lj} Small cap/BILLIONS. set SB' % cmi_debug )

            if MILLIONS:
                mktcap_clean = np.float(re.sub('M', '', mktcap))
                mb = "SM"
                logging.info( f'%s - {x} / {co_sym_lj} Large cap/MILLIONS. set SM' % cmi_debug )

            if not TRILLIONS and not BILLIONS and not MILLIONS:
                mktcap_clean = 0    # error condition - possible bad data
                mb = "SZ"           # Zillions
                logging.info( f'%s - {x} / {co_sym_lj} bad mktcap data N/A setting to SZ' % cmi_debug )
                # handle bad data in mktcap html page field

            if pct_val == "N/A":
                pct_val = float(0.0)        # Bad data. FOund a filed with N/A instead of read num
            else:
                pct_cl = re.sub('[\%\+\-]', "", pct_val )
                pct_clean = float(pct_cl)

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

            """
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
