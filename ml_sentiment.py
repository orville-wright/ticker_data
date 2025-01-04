#! /home/orville/venv/devel/bin/python3
import requests
from requests import Request, Session
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, date
import hashlib
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
from rich import print

from ml_yahoofinews import yfnews_reader
from ml_urlhinter import url_hinter
from y_topgainers import y_topgainers

# ML / NLP section #############################################################
class ml_sentiment:
    """
    Class to manage the Global Database of NLP Sentiment data
    and provide statistical analysis of sentiment
    """

    # global accessors
    args = []            # class dict to hold global args being passed in from main() methods
    yfn = None           # Yahoo Finance News reader instance
    mlnlp_uh = None      # URL Hinter instance
    sen_df0 = None
    sen_df1 = None
    row_count = 0
    yti = 0
    cycle = 0            # class thread loop counter

    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )

        self.args = global_args                            # Only set once per INIT. all methods are set globally
        self.yti = yti
        yfn = yfnews_reader(1, "IBM", global_args )        # instantiate a class of fyn with dummy info
        self.sen_df0 = pd.DataFrame(columns=[ 'Sym', 'Art', 'Chunk', 'Sent', 'Rank'] )
        return



##################################### 1 ####################################
    def save_sentiment(self, yti, data_set):
        """
        Save key ML sentiment info to global sentimennt Dataframe
        """
        self.yti = yti
        cmi_debug = __name__+"::"+self.save_sentiment.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        x = self.row_count      # get last row added to DF
        x += 1

        ################################ 6 ####################################
        # now construct our list for concatinating to the dataframe 
        logging.info( f"%s ============= Data prepared for DF =============" % cmi_debug )

        # sen_package = dict(sym=symbol, article=item_idx, chunk=i, sent=sen_result['label'], rank=raw_score )

        self.sen_data = [ \
                    x, \
                    data_set["sym"], \
                    data_set["article"], \
                    data_set["chunk"], \
                    data_set["sent"], \
                    data_set["rank"] ]
        
        print ( f"### DEBUG:: Sentiment database insert: {self.sen_data}" )

        ################################ 6 ####################################
        #self.df_1_row = pd.DataFrame(self.list_data, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time' ], index=[x] )
        #self.tg_df0 = pd.concat([self.tg_df0, self.df_1_row])  
        self.row_count = x

        return