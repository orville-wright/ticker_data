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
    all_tag_tr = ""       # BS4 handle of the <tr> extracted data
    td_tag_rows = ""      # BS4 handle of the <tr> extracted data
    tag_tbody = ""        # BS4 full body handle
    yti = 0
    cycle = 0           # class thread loop counter
    dummy_url = "https://finance.yahoo.com/screener/predefined/day_gainers"

    yahoo_headers = { \
                        'authority': 'finance.yahoo.com', \
                        'path': '/screener/predefined/day_gainers/', \
                        'referer': 'https://finance.yahoo.com/screener/', \
                        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"', \
                        'sec-ch-ua-mobile': '"?0"', \
                        'sec-fetch-mode': 'navigate', \
                        'sec-fetch-user': '"?1', \
                        'sec-fetch-site': 'same-origin', \
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' }
    
#####################################################
# init
    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INSTANTIATE' % cmi_debug )
        # init empty DataFrame with present colum names
        self.dg1_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.dg1_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.dg1_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.yti = yti
        return

    def init_dummy_session(self):
        self.dummy_resp0 = requests.get(self.dummy_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 )
        hot_cookies = requests.utils.dict_from_cookiejar(self.dummy_resp0.cookies)
        print ( f"cookie jar:")
        print ( f"{hot_cookies} ")
        #self.js_session.cookies.update({'A1': self.js_resp0.cookies['A1']} )    # yahoo cookie hack
        return

#####################################################
# method #1
    def get_data(self, yti):
        """
        Connect to finance.yahoo.com and extract (scrape) the raw string data out of
        the webpage data tables. Returns a BS4 handle.
        Send hint which engine processed & rendered the html page
        0. Simple HTML engine
        1. JAVASCRIPT HTML render engine (down redering a complex JS page in to simple HTML)
        """
        self.yti = yti
        cmi_debug = __name__+"::"+self.get_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        logging.info('%s - get using simple html engine..' % cmi_debug )
        #r = requests.get("https://finance.yahoo.com/gainers/" )
        r = requests.get("https://finance.yahoo.com/screener/predefined/small_cap_gainers/" )
        logging.info( "%s - html stream read completed" % cmi_debug )

        logging.info( f"%s - BS4 stream processing..." % cmi_debug )
        self.soup = BeautifulSoup(r.text, 'html.parser')
        self.tag_tbody = self.soup.find('tbody')
        self.tr_rows = self.tag_tbody.find(attrs={"class": "simpTblRow"})
        #self.all_tag_tr = self.soup.find(attrs={"class": "simpTblRow"})
        logging.info('%s Page processed by BS4 engine' % cmi_debug )
        return

#####################################################
# method #2
    def build_df0(self):
        """
        Build-out a fully populated Pandas DataFrame containg all the extracted/scraped fields from the
        html/markup table data Wrangle, clean/convert/format the data correctly.
        """

        cmi_debug = __name__+"::"+self.build_df0.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop all rows from DF0' % cmi_debug )
        self.dg1_df0 = pd.DataFrame()                                 # new df, but is NULLed
        x = 0

        # >>>DEBUG<< for when yahoo.com changes data model...
        print ( f"===== Rows: {len(self.tag_tbody.find_all('tr'))}  =================" )
        for j in self.tag_tbody.find_all('tr'):
            #"""
            # >>>DEBUG<< for when yahoo.com changes data model...
            y = 1
            for i in j.find_all('td'):
                print ( f"Data {y}: {i.text}" )
                #logging.info( f"%s - Data: {j.td.strings}" % cmi_debug )
                y += 1
            # >>>DEBUG<< for when yahoo.com changes data model...
            #"""
            extr_strs = j.strings
            co_sym = next(extr_strs)             # 1 : ticker symbol info / e.g "NWAU"
            co_name = next(extr_strs)            # 2 : company name / e.g "Consumer Automotive Finance, Inc."
            price = next(extr_strs)              # 3 : price (Intraday) / e.g "0.0031"

            change_sign = next(extr_strs)        # 4.0 : $ change sign [+/-] / e.g  "+0.0021"
            if change_sign == "+" or change_sign == "-":
                change_val = next(extr_strs)     # 4.1 : $ change value / e.g  "+0.0021"
            else:
                change_val = change_sign
                logging.info( f"{cmi_debug} : {co_sym} : no dedicated [+-] field for $ CHANGE" )
                if (re.search('\+', change_val)) or  (re.search('\-', change_val)) is True:
                    logging.info( f"{cmi_debug} : {change_val} : $ CHANGE is signed [+-], stripping..." )
                    change_cl = re.sub('[\+\-]', "", change_val)       # remove =/- sign
                    logging.info( f"%s : $ CHANGE cleaned: {change_cl}" % cmi_debug )
                else:
                    logging.info( f"{cmi_debug} - {change_val} : $ CHANGE is NOT signed [+-]" )
                    change_cl = re.sub('[\,]', "", change_val)       # remove ,
                    logging.info( f"%s : CHANGE cleaned: {change_cl}" % cmi_debug )
            # is there a dedicated collumn to hold a +/- indicator
            pct_sign = next(extr_strs)           # 5.0 : % change sign [+/-] / e.g "+%12.3"
            if pct_sign == "+" or pct_sign == "-":
                logging.info( f"{cmi_debug} : {change_val} : % CHANGE is signed [+-], skipping..." )
                #pct_cl = (re.sub('\+\-,', '', pct_sign))   # skipp
                pct_val = next(extr_strs)        # 5.1 : change / e.g "210.0000%" WARN trailing "%" must be removed before casting to float
            else:
                z = 0
                pct_val = pct_sign
                logging.info( f"{cmi_debug} : {co_sym} : Found no [+-] tag for % CHANGE" )

            vol = next(extr_strs)            # 6 : volume with scale indicator/ e.g "70.250k"
            avg_vol = next(extr_strs)        # 7 : Avg. vol over 3 months) / e.g "61,447"
            mktcap = next(extr_strs)         # 8 : Market cap with scale indicator / e.g "15.753B"
            peratio = next(extr_strs)        # 9 : PE ratio TTM (Trailing 12 months) / e.g "N/A"
            #mini_gfx = next(extr_strs)      # 10 : IGNORED = mini-canvas graphic 52-week rnage (no TXT/strings avail)

            ####################################################################
            # now wrangle the data...
            co_sym_lj = f"{co_sym:<6}"                                   # left justify TXT in DF & convert to raw string
            co_name_lj = np.array2string(np.char.ljust(co_name, 25) )    # left justify TXT in DF & convert to raw string
            co_name_lj = (re.sub('[\'\"]', '', co_name_lj) )             # remove " ' and strip leading/trailing spaces
            price_cl = re.sub('[\,]', "", price)                      # remove , seperator
            price_clean = float(price_cl)
            change_clean = float(change_val)

            if pct_val == "N/A":
                pct_val = float(0.0)                               # Bad data. FOund a filed with N/A instead of read num
            else:
                pct_cl = re.sub('[\%\+\-,]', "", pct_val )
                pct_clean = float(pct_cl)

            mktcap = (re.sub('[N\/A]', '0', mktcap))               # handle N/A
            TRILLIONS = re.search('T', mktcap)
            BILLIONS = re.search('B', mktcap)
            MILLIONS = re.search('M', mktcap)

            if TRILLIONS:
                mktcap_clean = float(re.sub('T', '', mktcap))
                mb = "ST"
                logging.info( f'%s - {x} / {co_sym_lj} Small Cap/TRILLIONS. set ST' % cmi_debug )

            if BILLIONS:
                mktcap_clean = float(re.sub('B', '', mktcap))
                mb = "SB"
                logging.info( f'%s - {x} / {co_sym_lj} Small cap/BILLIONS. set SB' % cmi_debug )

            if MILLIONS:
                mktcap_clean = float(re.sub('M', '', mktcap))
                mb = "SM"
                logging.info( f'%s - {x} / {co_sym_lj} Large cap/MILLIONS. set SM' % cmi_debug )

            if not TRILLIONS and not BILLIONS and not MILLIONS:
                mktcap_clean = 0    # error condition - possible bad data
                mb = "SZ"           # Zillions
                logging.info( f'%s - {x} - {co_sym_lj} bad mktcap data N/A - SZ' % cmi_debug )
                # handle bad data in mktcap html page field

            logging.info( f"%s === Data prepared for DF" % cmi_debug )

            self.list_data = [[ \
                       x, \
                       re.sub('\'', '', co_sym_lj), \
                       co_name_lj, \
                       price_clean, \
                       change_clean, \
                       pct_clean, \
                       mktcap_clean, \
                       mb, \
                       time_now ]]

            # convert our list into a 1 row dataframe
            self.df_1_row = pd.DataFrame(self.list_data, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time' ], index=[x] )
            self.dg1_df0 = pd.concat([self.dg1_df0, self.df_1_row])
            x+=1

        logging.info('%s - populated new DF0 dataset' % cmi_debug )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)
                        # sucess = lobal class accessor (y_topgainers.*_df0) populated & updated

# ##############################################################################
# method #3
# Hacking function - keep me arround for a while
    def prog_bar(self, x, y):
        """simple progress dialogue function"""
        if x % y == 0:
            print ( " " )
        else:
            print ( ".", end="" )
        return

#####################################################
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

#####################################################
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

#####################################################
# method #7
    def print_top10(self):
        """Prints the Top 20 Dataframe"""

        cmi_debug = __name__+"::"+self.print_top10.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.dg1_df1.sort_values(by='Pct_change', ascending=False ) )
        return

#####################################################
# method #6
    def build_10ten60(self, cycle):
        """Build-up 10x10x060 historical DataFrame (df2) from source df1"""
        """Generally called on some kind of cycle"""

        cmi_debug = __name__+"::"+self.build_10ten60.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        self.dg1_df2 = self.dg1_df2.append(self.dg1_df1, ignore_index=False)    # merge top 10 into
        self.dg1_df2.reset_index(inplace=True, drop=True)    # ensure index is allways unique + sequential
        return

#####################################################
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

        lowsym_ser = self.dg1_df1.iloc[minv, :]
        lowsym = lowsym_ser.iloc[1]
        lowconame = lowsym_ser.iloc[2]
        lowpctchange = lowsym_ser.iloc[5]

        print ( "=============================================================================")


        # Allways make sure this is key #1 in the recommendations dict
        rx['1'] = ('Small cap % gainer:', lowsym.rstrip(), '$'+str(ulp), lowconame.rstrip(), '+%'+str(lowpctchange) )

        print ( f"Best low-buy OPPTY: #{minv} | {lowconame.rstrip()} ({lowsym.rstrip()}) | ${lowestprice} | %{lowpctchange}" )
        print ( " " )
        print ( self.dg1_df1 )
        return rx       # dict{}
