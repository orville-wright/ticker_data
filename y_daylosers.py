#!/home/orville/venv/devel/bin/python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
from rich import print

logging.basicConfig(level=logging.INFO)

#####################################################
class y_daylosers:
    """Class to extract Top Losers data set from finance.yahoo.com"""
    # global accessors
    tl_df0 = ""          # DataFrame - Full list of top loserers
    tl_df1 = ""          # DataFrame - Ephemerial list of top 10 loserers. Allways overwritten
    tl_df2 = ""          # DataFrame - Top 10 ever 10 secs for 60 secs
    all_tag_tr = ""      # BS4 handle of the <tr> extracted data
    rows_extr = 0        # number of rows of data extracted
    ext_req = ""         # request was handled by y_cookiemonster
    yti = 0
    cycle = 0            # class thread loop counter

    dummy_url = "https://finance.yahoo.com/screener/predefined/day_losers"

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

    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
        # init empty DataFrame with present colum names
        self.tl_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.tl_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' 'Mkt_cap', 'M_B', 'Time'] )
        self.tl_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' 'Mkt_cap', 'M_B', 'Time'] )
        self.yti = yti
        return


# method #1
    def init_dummy_session(self):
        self.dummy_resp0 = requests.get(self.dummy_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 )
        hot_cookies = requests.utils.dict_from_cookiejar(self.dummy_resp0.cookies)
        #self.js_session.cookies.update({'A1': self.js_resp0.cookies['A1']} )    # yahoo cookie hack
        return

# method #2
    def ext_get_data(self, yti):
        """
        Connect to finance.yahoo.com and extract (scrape) the raw string data out of
        the webpage data tables. Returns a BS4 handle.
        Send hint which engine processed & rendered the html page
        0. Simple HTML engine
        1. JAVASCRIPT HTML render engine (down redering a complex JS page in to simple HTML)
        """
        self.yti = yti
        cmi_debug = __name__+"::"+self.ext_get_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        logging.info('%s - ext request pre-processed by cookiemonster...' % cmi_debug )
        # use an existing resposne from a previously managed req (handled by cookie monster) 
        r = self.ext_req
        logging.info( f"%s - BS4 stream processing..." % cmi_debug )
        self.soup = BeautifulSoup(r.text, 'html.parser')
        self.tag_tbody = self.soup.find('tbody')
        self.tr_rows = self.tag_tbody.find_all("tr")
        logging.info('%s Page processed by BS4 engine' % cmi_debug )
        return

# method #3
    def build_tl_df0(self):
        """
        Build-out a fully populated Pandas DataFrame containg all the extracted/scraped fields from the
        html/markup table data Wrangle, clean/convert/format the data correctly.
        """

        cmi_debug = __name__+"::"+self.build_tl_df0.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Create clean NULL DataFrame' % cmi_debug )
        self.tl_df0 = pd.DataFrame()             # new df, but is NULLed
        x = 0
        self.rows_extr = int( len(self.tag_tbody.find_all('tr')) )

        for datarow in self.tr_rows:

            """
            # >>>DEBUG<< for whedatarow.stripped_stringsn yahoo.com changes data model...
            y = 1
            print ( f"===================== Debug =========================" )
            #print ( f"Data {y}: {datarow}" )
            for i in datarow.find_all("td"):
                print ( f"===================================================" )
                if i.canvas is not None:
                    print ( f"Data {y}: Found Canvas, skipping..." )
                else:
                    print ( f"Data {y}: {i.text}" )
                    print ( f"Data g: {next(i.stripped_strings)}" )
                #logging.info( f'%s - Data: {debug_data.strings}' % cmi_debug )
                y += 1
            print ( f"===================== Debug =========================" )
            # >>>DEBUG<< for when yahoo.com changes data model...
            """

            # Data Extractor Generator
            def extr_gen():
                for i in datarow.find_all("td"):
                    if i.canvas is not None:
                        yield ( f"canvas" )
                    else:
                        yield ( f"{next(i.stripped_strings)}" )

            ################################ 1 ####################################
            extr_strs = extr_gen()
            co_sym = next(extr_strs)             # 1 : ticker symbol info / e.g "NWAU"
            co_name = next(extr_strs)            # 2 : company name / e.g "Consumer Automotive Finance, Inc."
            mini_chart = next(extr_strs)         # 3 : embeded mini GFX chart
            price = next(extr_strs)              # 3 : price (Intraday) / e.g "0.0031"

            ################################ 2 ####################################

            change_sign = next(extr_strs)        # 4 : test for dedicated column for +/- indicator
            logging.info( f"{cmi_debug} : {co_sym} : Check dedicated [+-] field for $ CHANGE" )
            if change_sign == "+" or change_sign == "-":    # 4 : is $ change sign [+/-] a dedciated field
                change_val = next(extr_strs)                # 4 : Yes, advance iterator to next field (ignore dedciated sign field)
            else:
                change_val = change_sign                    # 4 : get $ change, but its possibly +/- signed
                if (re.search(r'\+', change_val)) or (re.search(r'\-', change_val)) is not None:
                    logging.info( f"{cmi_debug} : {change_val} : $ CHANGE is signed [+-], stripping..." )
                    change_cl = re.sub(r'[\+\-]', "", change_val)       # remove +/- sign
                    logging.info( f"%s : $ CHANGE +/- cleaned : {change_cl}" % cmi_debug )
                else:
                    logging.info( f"{cmi_debug} : {change_val} : $ CHANGE is NOT signed [+-]" )
                    change_cl = re.sub(r'[\,]', "", change_val)       # remove
                    logging.info( f"%s : $ CHANGE , cleaned : {change_cl}" % cmi_debug )

            pct_sign = next(extr_strs)              # 5 : test for dedicated column for +/- indicator
            logging.info( f"{cmi_debug} : {co_sym} : Check dedicated [+-] field for % CHANGE" )
            if pct_sign == "+" or pct_sign == "-":  # 5 : is %_change sign [+/-] a dedciated field
                pct_val = next(extr_strs)           # 5 : advance iterator to next field (ignore dedciated sign field)
            else:
                pct_val = pct_sign                  # 5 get % change, but its possibly +/- signed
                if (re.search(r'\+', pct_val)) or (re.search(r'\-', pct_val)) is not None:
                    logging.info( f"{cmi_debug} : {pct_val} : % CHANGE is signed [+-], stripping..." )
                    pct_cl = re.sub(r'[\+\-\%]', "", pct_val)       # remove +/-/% signs
                    logging.info( f"{cmi_debug} : % CHANGE cleaned to: {pct_cl}" )
                else:
                    logging.info( f"{cmi_debug} : {pct_val} : % CHANGE is NOT signed [+-]" )
                    change_cl = re.sub(r'[\,\%]', "", pct_val)       # remove
                    logging.info( f"{cmi_debug} : % CHANGE: {pct_val}" )

            ################################ 3 ####################################
            vol = next(extr_strs)            # 6 : volume with scale indicator/ e.g "70.250k"
            avg_vol = next(extr_strs)        # 7 : Avg. vol over 3 months) / e.g "61,447"
            mktcap = next(extr_strs)         # 8 : Market cap with scale indicator / e.g "15.753B"
            peratio = next(extr_strs)        # 9 : PE ratio TTM (Trailing 12 months) / e.g "N/A"
            #mini_gfx = next(extr_strs)      # 10 : IGNORED = mini-canvas graphic 52-week rnage (no TXT/strings avail)

            ################################ 4 ####################################
            # now wrangle the data...
            co_sym_lj = f"{co_sym:<6}"                                   # left justify TXT in DF & convert to raw string
            co_name_lj = np.array2string(np.char.ljust(co_name, 60) )    # left justify TXT in DF & convert to raw string
            co_name_lj = (re.sub(r'[\'\"]', '', co_name_lj) )             # remove " ' and strip leading/trailing spaces     
            price_cl = (re.sub(r'\,', '', price))                         # remove ,
            price_clean = float(price_cl)
            change_clean = float(change_val)

            if pct_val == "N/A":
                pct_val = float(0.0)                               # Bad data. FOund a filed with N/A instead of read num
            else:
                pct_cl = re.sub(r'[\%\+\-,]', "", pct_val )
                pct_clean = float(pct_cl)

            ################################ 5 ####################################
            mktcap = (re.sub(r'[N\/A]', '0', mktcap))               # handle N/A
            TRILLIONS = re.search('T', mktcap)
            BILLIONS = re.search('B', mktcap)
            MILLIONS = re.search('M', mktcap)

            if TRILLIONS:
                mktcap_clean = float(re.sub('T', '', mktcap))
                mb = "LT"
                logging.info( f'%s : #{x} : {co_sym_lj} Mkt Cap: TRILLIONS : T' % cmi_debug )

            if BILLIONS:
                mktcap_clean = float(re.sub('B', '', mktcap))
                mb = "LB"
                logging.info( f'%s : #{x} : {co_sym_lj} Mkt cap: BILLIONS : B' % cmi_debug )

            if MILLIONS:
                mktcap_clean = float(re.sub('M', '', mktcap))
                mb = "LM"
                logging.info( f'%s : #{x} : {co_sym_lj} Mkt cap: MILLIONS : M' % cmi_debug )

            if not TRILLIONS and not BILLIONS and not MILLIONS:
                mktcap_clean = 0    # error condition - possible bad data
                mb = "LZ"           # Zillions
                logging.info( f'%s : #{x} : {co_sym_lj} bad mktcap data N/A : Z' % cmi_debug )
                # handle bad data in mktcap html page field

            ################################ 6 ####################################
            # now construct our list for concatinating to the dataframe 
            logging.info( f"%s ============= Data prepared for DF =============" % cmi_debug )

            self.list_data = [[ \
                       x, \
                       re.sub(r'\'', '', co_sym_lj), \
                       co_name_lj, \
                       price_clean, \
                       change_clean, \
                       pct_clean, \
                       mktcap_clean, \
                       mb, \
                       time_now ]]

            ################################ 7 ####################################
            self.df_1_row = pd.DataFrame(self.list_data, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time' ], index=[x] )
            self.tl_df0 = pd.concat([self.tl_df0, self.df_1_row])
            x+=1

        logging.info('%s - populated new DF0 dataset' % cmi_debug )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)
                        # sucess = lobal class accessor (y_topgainers.*_df0) populated & updated

# method #4
    def topg_listall(self):
        """
        Print the full DataFrame table list of Yahoo Finance Top loserers
        Sorted by % Change
        """

        cmi_debug = __name__+"::"+self.topg_listall.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.tl_df0.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built
        return

# method #5
    def build_top10(self):
        """
        Get top 10 loserers from main DF (df0) -> temp DF (df1)
        Number of rows to grab is now set from num of rows that BS4 actually extracted (rows_extr)
        df1 is ephemerial. Is allways overwritten on each run
        """

        cmi_debug = __name__+"::"+self.build_top10.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        logging.info('%s - Drop all rows from DF1' % cmi_debug )
        self.tl_df1.drop(self.tl_df1.index, inplace=True)
        logging.info('%s - Copy DF0 -> ephemerial DF1' % cmi_debug )
        self.tl_df1 = self.tl_df0.sort_values(by='Pct_change', ascending=False ).head(self.rows_extr).copy(deep=True)    # create new DF via copy of top 10 entries
        self.tl_df1.rename(columns = {'Row':'ERank'}, inplace = True)   # Rank is more accurate for this Ephemerial DF
        self.tl_df1.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        return

# method #6
    def print_top10(self):
        """
        Prints the Top 10 Dataframe
        Number of rows to grab is now set from num of rows that BS4 actually extracted (rows_extr)
        """

        cmi_debug = __name__+"::"+self.print_top10.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( f"{self.tl_df1.sort_values(by='Pct_change', ascending=False ).head(self.rows_extr)}" )
        return

# method #7
    def build_tenten60(self, cycle):
        """
        Build-up 10x10x060 historical DataFrame (df2) from source df1
        Generally called on some kind of cycle
        """

        cmi_debug = __name__+"::"+self.build_tenten60.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        self.tl_df2 = self.tl_df2.append(self.tl_df1, ignore_index=False)    # merge top 10 into
        self.tl_df2.reset_index(inplace=True, drop=True)    # ensure index is allways unique + sequential
        return
