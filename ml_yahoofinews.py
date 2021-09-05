#!/usr/bin/python3
import requests
from requests import Request, Session
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
import threading
import json

from bigcharts_md import bc_quote

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class yfnews_reader:
    """
    Read Yahoo Finance news reader, Word Vectorizer, Positive/Negative sentiment analyzer
    """

    # global accessors
    symbol = ""             # Unique company symbol
    js_session = ""         # main requests session
    yfn_df0 = ""            # DataFrame 1
    yfn_df1 = ""            # DataFrame 2
    yfn_all_data =""        # JSON dataset contains ALL data
    yfn_pridata = ""
    ml_brief = []           # ML TXT matrix for Naieve Bayes Classifier pre Count Vectorizer
    ul_tag_dataset = ""     # BS4 handle of the <tr> extracted data
    inst_uid = 0
    yti = 0                 # Unique instance identifier
    cycle = 0               # class thread loop counter
    soup = ""               # BS4 shared handle between UP & DOWN (1 URL, 2 embeded data sets in HTML doc)
    args = []               # class dict to hold global args being passed in from main() methods

                            # yahoo.com header/cookie hack
    yahoo_headers = { \
                    'authority': 'yahoo.com', \
                    'path': '/v1/finance/trending/US?lang=en-US&region=US&count=5&corsDomain=finance.yahoo.com', \
                    'origin': 'https://finance.yahoo.com', \
                    'referer': 'https://finance.yahoo.com/', \
                    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"', \
                    'sec-ch-ua-mobile': '"?0"', \
                    'sec-fetch-mode': 'cors', \
                    'sec-fetch-site': 'cross-site', \
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' }


    def __init__(self, yti, symbol, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INIT' % cmi_debug )
        # init empty DataFrame with preset colum names
        self.args = global_args
        self.symbol = symbol
        #self.up_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', "Vol", 'Vol_pct', 'Time' ] )
        #self.down_df1 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', "Vol", 'Vol_pct', 'Time' ] )
        #self.df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', "Vol", 'Vol_pct', 'Time' ] )
        self.yti = yti
        self.js_session = HTMLSession()                        # init JAVAScript processor early
        self.js_session.cookies.update(self.yahoo_headers)     # load cookie/header hack data set into session
        return

# method #1
    def yfn_getdata(self):
        """
        Initial blind intro to yahoo.com/news JAVASCRIPT page
        BeautifulSoup scraping requires on JS processed page.
        note: Javascript engine is required, Cant process/read a JS page via requests().
        """

        cmi_debug = __name__+"::"+self.yfn_getdata.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        # Initial blind get
        # present ourself to NASDAQ.com so we can extract the critical cookie -> ak_bmsc
        # be nice and set a healthy cookie package
        logging.info('%s - blind intro get()' % cmi_debug )
        self.js_session.cookies.update(self.yahoo_headers)    # redundent as it's done in INIT but I'm not sure its persisting from there
        with self.js_session.get("https://www.finance.yahoo.com", stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - EXTRACT/INSERT 8 special cookies  ' % cmi_debug )
            self.js_session.cookies.update({'APID': self.js_resp0.cookies['APID']} )    # NASDAQ cookie hack
            self.js_session.cookies.update({'d': self.js_resp0.cookies['d']} )    # NASDAQ cookie hack
            self.js_session.cookies.update({'v': self.js_resp0.cookies['v']} )    # NASDAQ cookie hack
            self.js_session.cookies.update({'A1': self.js_resp0.cookies['A1']} )    # NASDAQ cookie hack
            self.js_session.cookies.update({'A3': self.js_resp0.cookies['A3']} )    # NASDAQ cookie hack
            self.js_session.cookies.update({'GUC': self.js_resp0.cookies['GUC']} )    # NASDAQ cookie hack
            self.js_session.cookies.update({'t': self.js_resp0.cookies['t']} )    # NASDAQ cookie hack
            self.js_session.cookies.update({'APIDTS': self.js_resp0.cookies['APIDTS']} )    # NASDAQ cookie hack

        # 2nd get with the secret yahoo.com cookie now inserted
        # NOTE: Just the finaince.Yahoo.com MAIN landing page - generic news
        logging.info('%s - rest API read json' % cmi_debug )
        with self.js_session.get("https://www.finance.yahoo.com", stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp2:
            # read the webpage with our Javascript engine processor
            logging.info('%s - Javascript engine processing...' % cmi_debug )
            self.js_resp2.html.render()    # might now even be needed now that nasdaq REST API get is working
            logging.info('%s - Javascript engine completed!' % cmi_debug )

            # we can access pure 'Unusual VOlume' JSON data via an authenticated/valid REST API call
            logging.info('%s - json data extracted' % cmi_debug )
            logging.info('%s - store FULL json dataset' % cmi_debug )
            # self.uvol_all_data = json.loads(self.js_resp2.text)
            logging.info('%s - store data 1' % cmi_debug )
            # self.uvol_up_data =  self.uvol_all_data['data']['up']['table']['rows']
            logging.info('%s - store data 2' % cmi_debug )
            # self.uvol_down_data = self.uvol_all_data['data']['down']['table']['rows']

         # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"================================ {self.yti} ======================================" )
            print ( f"=== session cookies ===\n" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )

        return
