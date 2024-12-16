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
class ml_nlpreader:
    """
    Class to identify, rank, classifcy stocks to read
    """

    # global accessors
    args = []            # class dict to hold global args being passed in from main() methods
    yfn = ""
    uh = ""              # URL Hinter
    yti = 0
    cycle = 0            # class thread loop counter

    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )

        self.args = global_args                            # Only set once per INIT. all methods are set globally
        self.yti = yti
        yfn = yfnews_reader(1, "IBM", global_args )        # instantiate a class of fyn with dummy info
        return

########################################## 1 #############################################
# method 1
    def nlp_read_all(self, global_args):
        """
        The machine will read now!
        Read finance.yahoo.com / News 'Brief headlines' (i.e. short text docs) 
        Reads new for ALL stock symbols in the Top Gainers DF table.
        """

        self.args = global_args
        if self.args['bool_news'] is True:                   # read ALL news for top 10 gainers
            cmi_debug = __name__+"::"+self.nlp_read_all.__name__+".#"+str(self.yti)
            logging.info( f'%s - Instantiate.#{self.yti}' % cmi_debug )
            print ( " " )
            print ( "========================= ML (NLP) / Yahoo Finance News Sentiment AI =========================" )
            print ( f"Build NLP test dataset / for Top Gainers..." )
            newsai_test_dataset = y_topgainers(2)       # instantiate class
            newsai_test_dataset.get_topg_data()         # extract data from finance.Yahoo.com
            nx = newsai_test_dataset.build_tg_df0()     # build entire dataframe
            newsai_test_dataset.build_top10()           # build top 10 gainers
            print ( " " )
            yfn = yfnews_reader(1, "IBM", self.args )   # dummy symbol just for instantiation
            yfn.init_dummy_session()
            #yfn.yfn_bintro()
            uh = url_hinter(1, self.args)               # anyone needs to be able to get hints on a URL from anywhere
            yfn.share_hinter(uh)                        # share the url hinter available
            print ( "============================== Prepare bulk NLP candidate list =================================" )
            print ( f"ML/NLP candidates: {newsai_test_dataset.tg_df1['Symbol'].tolist()}" )
            for nlp_target in newsai_test_dataset.tg_df1['Symbol'].tolist():
                yfn.update_headers(nlp_target)
                yfn.form_url_endpoint(nlp_target)
                yfn.do_simple_get()
                yfn.scan_news_feed(nlp_target, 0, 0)    # (params) #1: level, #2: [0=HTML / 1=JavaScript]
                yfn.eval_article_tags(nlp_target)       # ml_ingest{} is built
                print ( "============================== NLP candidates are ready =================================" )

            self.nlp_summary(2)
            print ( f" " )
            print ( " " )
            print ( "========================= Tech Events performance Sentiment =========================" )

        return

########################################## 2 #############################################
# method #2
    def nlp_read_one(self, news_symbol, global_args):
        """
        The machine will read now!
        Read finance.yahoo.com / News 'Brief headlines' (i.e. short text docs) 
        Reads news for only ONE stock symbol.
        """

        self.args = global_args

        cmi_debug = __name__+"::"+self.nlp_read_one.__name__+".#"+str(self.yti)
        logging.info( f'%s - IN.#{self.yti}' % cmi_debug )
        news_symbol = str(self.args['newsymbol'])       # symbol provided on CMDLine
        print ( " " )
        print ( f"========================= ML (NLP) / News Sentiment AI {news_symbol} =========================" )
        yfn = yfnews_reader(1, news_symbol, self.args )  # dummy symbol just for instantiation
        yfn.init_dummy_session()
        #yfn.yfn_bintro()
        yfn.update_headers(news_symbol)
        yfn.form_url_endpoint(news_symbol)
        yfn.do_js_get()                         # get() & process the page html/JS data
        uh = url_hinter(1, self.args)           # anyone needs to be able to get hints on a URL from anywhere
        yfn.share_hinter(uh)
        yfn.scan_news_feed(news_symbol, 0, 1)   #  p0: symbol - p1: Level - p2: [0=HTML / 1=JavaScript]
        yfn.eval_article_tags(news_symbol)      # ml_ingest{} is built
        print ( f" " )
        print ( "========================= Evaluate quality of ML/NLP candidates =========================" )

        self.nlp_summary(3)
        print ( f" " )

        return

####################################### 3 ##########################################
# method 3
    def nlp_summary(self, yti):
        """
        NLP Support function
        **CRTIICAL: Assumes ml_ingest has  already been pre-populated
        Cycles thru each .item in in the ml_ingest{} and processes it...
        Prints a nice sumamry of each NLP candidates in ml_digest{}
        """

        self.yti = yti
        cmi_debug = __name__+"::"+self.nlp_summary.__name__+".#"+str(self.yti)
        logging.info( f'%s - IN.#{yti}' % cmi_debug )
        logging.info('%s - ext get request pre-processed by cookiemonster...' % cmi_debug )
        locality_code = {
                    0: 'Local 0',
                    1: 'Local 1',
                    2: 'Local 2',
                    3: 'Remote',
                    9: 'Unknown locality'
                    }

        print ( " ")
        print ( f"====================== Depth 2 ======================" )
        cmi_debug = __name__+"::nlp_summary().#1"
        for sn_idx, sn_row in self.yfn.ml_ingest.items():                       # cycle thru the NLP candidate list
            if sn_row['type'] == 0:                                             # REAL news, inferred from Depth 0
                print( f"News article:  {sn_idx} / {sn_row['symbol']} / ", end="" )
                t_url = urlparse(sn_row['url'])                                 # WARN: a rlparse() url_named_tupple (NOT the raw url)
                uhint, uhdescr = self.uh.uhinter(20, t_url)
                thint = (sn_row['thint'])                                       # the hint we guessed at while interrogating page <tags>
                logging.info ( f"%s - Logic.#0 hinting origin url: t:0 / u:{uhint} / h: {thint} {uhdescr}" % cmi_debug )
                r_uhint, r_thint, r_xturl = self.yfn.interpret_page(sn_idx, sn_row)    # go deep, with everything we knonw about this item
                p_r_xturl = urlparse(r_xturl)
                inf_type = self.yfn.uh.confidence_lvl(thint)     # returned var is a tupple
                #
                print ( f"- NLP candidate" )                # all type 0 are assumed to be REAL news
                print ( f"Origin URL:    [ {t_url.netloc} ] / {uhdescr} / {inf_type[0]} / ", end="" )
                print ( f"{locality_code.get(inf_type[1])}" )
                uhint, uhdescr = self.uh.uhinter(21, p_r_xturl)
                print ( f"Target URL:    [ {p_r_xturl.netloc} ] / {uhdescr} / ", end="" )
                print ( f"{locality_code.get(uhint)} [ u:{uhint} ])" )
                print ( f"====================== Depth 2 ======================" )
                # summary report...
            elif sn_row['type'] == 1:                       # Micro-Ad, but could possibly be news...
                print( f"News article:  {sn_idx} / {sn_row['symbol']} /", end="" )
                t_url = urlparse(sn_row['url'])
                uhint, uhdescr = self.uh.uhinter(30, t_url)      # hint on ORIGIN url
                #thint = (sn_row['thint'])                   # the hint we guess at while interrogating page <tags>
                r_uhint, r_thint, r_xturl = self.yfn.interpret_page(sn_idx, sn_row)    # go deep, with everything we knonw about this item
                logging.info ( f"%s - Logic.#1 hinting origin url: t:1 / u:{r_uhint} / h: {r_thint} {uhdescr}" % cmi_debug )
                p_r_xturl = urlparse(r_xturl)
                inf_type = self.yfn.uh.confidence_lvl(r_thint)
                # summary report...
                print ( f"NLP candidate" )                      # all type 0 are assumed to be REAL news
                print ( f"Origin URL:    [ {t_url.netloc} ] / {uhdescr} / {inf_type[0]} / ", end="" )
                print ( f"{locality_code.get(inf_type[1], 'in flux')}" )
                uhint, uhdescr = self.uh.uhinter(31, p_r_xturl)      # hint on TARGET url
                print ( f"Target URL:    [ {p_r_xturl.netloc} ] / {uhdescr} / ", end="" )
                print ( f"{locality_code.get(uhint, 'in flux')} [ u:{uhint} ])" )
                print ( f"====================== Depth 2 ======================" )
                #
            elif sn_row['type'] == 2:                     # possibly not news? (Micro Ad)
                print ( f"Logic.#2 - Bulk injected - NOT an NLP candidate" )
                logging.info ( f"%s - #3 skipping..." % cmi_debug )
                print ( f"====================== Depth 2 ======================" )
                #
            elif sn_row['type'] == 9:                     # possibly not news? (Micro Ad)
                print ( f"Logic.#9 - Article type NOT yet define - NOT an NLP candidate" )
                logging.info ( f"%s - #3 skipping..." % cmi_debug )
                print ( f"====================== Depth 2 ======================" )
                #
            else:
                print ( f"Logic.#ERR - ERROR unknown article type in ml_ingest" )
                logging.info ( f"%s - #4 skipping..." % cmi_debug )
                print ( f"====================== Depth 2 ======================" )

        return