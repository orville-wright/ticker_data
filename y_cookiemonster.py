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

class y_cookiemonster:
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
    def get_scap_data(self):
        """Connect to finance.yahoo.com and extract (scrape) the raw sring data out of"""
        """the embedded webpage [Stock:Top Gainers] html data table. Returns a BS4 handle."""

        cmi_debug = __name__+"::"+self.get_scap_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        r = requests.get("https://finance.yahoo.com/gainers" )
        logging.info('%s - read html stream' % cmi_debug )
        self.soup = BeautifulSoup(r.text, 'html.parser')
        # ATTR style search. Results -> Dict
        # <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
        logging.info('%s - save data object handle' % cmi_debug )
        self.tag_tbody = self.soup.find('tbody')
        self.all_tag_tr = self.soup.find_all(attrs={"class": "simpTblRow"})   # simpTblRow
        #self.tr_rows = self.tag_tbody.find(attrs={"class": "simpTblRow"})

        print ( f">>> DEBUG:\n {r.text}" )

        logging.info('%s - close url handle' % cmi_debug )
        r.close()
        return