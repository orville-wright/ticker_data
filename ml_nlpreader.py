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

# ML / NLP section #############################################################
class ml_nlpreader:
    """Class to identify, rank, classifcy, impactfully real stock docs to read and 
    then read them.
    """
    # global accessors
    yti = 0
    cycle = 0            # class thread loop counter

    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
        # init empty DataFrame with present colum names
        self.tg_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.tg_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.tg_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.yti = yti
        return

#######################################################################################
# method #1

    def nlp_summary():
        """
        NLP Support function
        Assumes ml_ingest is already pre-built
        Cycles
        thru each item in the ml_ingest{} and processes...
        Prints a nice sumamry of each NLP candidates in ml_digest{}
        """
        locality_code = { 0: 'Local 0',
                    1: 'Local 1',
                    2: 'Local 2',
                    3: 'Remote',
                    9: 'Unknown locality'
                    }

        print ( " ")
        print ( f"====================== Depth 2 ======================" )
        cmi_debug = __name__+"::nlp_summary().#1"
        for sn_idx, sn_row in yfn.ml_ingest.items():                            # cycle thru the NLP candidate list
            if sn_row['type'] == 0:                                             # REAL news, inferred from Depth 0
                print( f"News article:  {sn_idx} / {sn_row['symbol']} / ", end="" )
                t_url = urlparse(sn_row['url'])                                 # WARN: a rlparse() url_named_tupple (NOT the raw url)
                uhint, uhdescr = uh.uhinter(20, t_url)
                thint = (sn_row['thint'])                                       # the hint we guessed at while interrogating page <tags>
                logging.info ( f"%s - Logic.#0 hinting origin url: t:0 / u:{uhint} / h: {thint} {uhdescr}" % cmi_debug )
                r_uhint, r_thint, r_xturl = yfn.interpret_page(sn_idx, sn_row)    # go deep, with everything we knonw about this item
                p_r_xturl = urlparse(r_xturl)
                inf_type = yfn.uh.confidence_lvl(thint)     # returned var is a tupple
                #
                print ( f"- NLP candidate" )                # all type 0 are assumed to be REAL news
                print ( f"Origin URL:    [ {t_url.netloc} ] / {uhdescr} / {inf_type[0]} / ", end="" )
                print ( f"{locality_code.get(inf_type[1])}" )
                uhint, uhdescr = uh.uhinter(21, p_r_xturl)
                print ( f"Target URL:    [ {p_r_xturl.netloc} ] / {uhdescr} / ", end="" )
                print ( f"{locality_code.get(uhint)} [ u:{uhint} ])" )
                print ( f"====================== Depth 2 ======================" )
                # summary report...
            elif sn_row['type'] == 1:                       # Micro-Ad, but could possibly be news...
                print( f"News article:  {sn_idx} / {sn_row['symbol']} /", end="" )
                t_url = urlparse(sn_row['url'])
                uhint, uhdescr = uh.uhinter(30, t_url)      # hint on ORIGIN url
                #thint = (sn_row['thint'])                   # the hint we guess at while interrogating page <tags>
                r_uhint, r_thint, r_xturl = yfn.interpret_page(sn_idx, sn_row)    # go deep, with everything we knonw about this item
                logging.info ( f"%s - Logic.#1 hinting origin url: t:1 / u:{r_uhint} / h: {r_thint} {uhdescr}" % cmi_debug )
                p_r_xturl = urlparse(r_xturl)
                inf_type = yfn.uh.confidence_lvl(r_thint)
                # summary report...
                print ( f"NLP candidate" )                      # all type 0 are assumed to be REAL news
                print ( f"Origin URL:    [ {t_url.netloc} ] / {uhdescr} / {inf_type[0]} / ", end="" )
                print ( f"{locality_code.get(inf_type[1], 'in flux')}" )
                uhint, uhdescr = uh.uhinter(31, p_r_xturl)      # hint on TARGET url
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

#######################################################################################
# method #2
# Read the news for multiple stock symbols

    def nlp_read_all():
        """
        The machine will read now!
        Read finance.yahoo.com / News 'Brief headlines' (i.e. short text docs) for ALL Top Gainer stocks.
        """

        if args['bool_news'] is True:                   # read ALL news for top 10 gainers
            cmi_debug = __name__+"::nlp_all.#1"
            print ( " " )
            print ( "========================= ML (NLP) / Yahoo Finance News Sentiment AI =========================" )
            print ( f"Build NLP test dataset / for Top Gainers..." )
            newsai_test_dataset = y_topgainers(2)       # instantiate class
            newsai_test_dataset.get_topg_data()         # extract data from finance.Yahoo.com
            nx = newsai_test_dataset.build_tg_df0()     # build entire dataframe
            newsai_test_dataset.build_top10()           # build top 10 gainers
            print ( " " )
            yfn = yfnews_reader(1, "IBM", args )        # dummy symbol just for instantiation
            yfn.init_dummy_session()
            #yfn.yfn_bintro()
            uh = url_hinter(1, args)        # anyone needs to be able to get hints on a URL from anywhere
            yfn.share_hinter(uh)                        # share the url hinter available
            print ( "============================== Prepare bulk NLP candidate list =================================" )
            print ( f"ML/NLP candidates: {newsai_test_dataset.tg_df1['Symbol'].tolist()}" )
            for nlp_target in newsai_test_dataset.tg_df1['Symbol'].tolist():
                yfn.update_headers(nlp_target)
                yfn.form_url_endpoint(nlp_target)
                yfn.do_simple_get()
                yfn.scan_news_feed(nlp_target, 0, 0)    # (params) #1: level, #2: 0=HTML / 1=JavaScript
                yfn.eval_article_tags(nlp_target)       # ml_ingest{} is built
                print ( "============================== NLP candidates are ready =================================" )

            nlp_summary()
            print ( f" " )
            print ( " " )
            print ( "========================= Tech Events performance Sentiment =========================" )

        return


#######################################################################################
# method #3
# Read the news for just 1 stock symbol
    def nlp_read_one():
        """
        The machine will read now!
        Read finance.yahoo.com / News 'Brief headlines' (i.e. short text docs) for ONE stock symbol.
        """
        if args['newsymbol'] is not False:
            cmi_debug = __name__+"::_args_newsymbol.#1"
            news_symbol = str(args['newsymbol'])       # symbol provided on CMDLine
            print ( " " )
            print ( f"========================= ML (NLP) / News Sentiment AI {news_symbol} =========================" )
            yfn = yfnews_reader(1, news_symbol, args )  # dummy symbol just for instantiation
            yfn.init_dummy_session()
            #yfn.yfn_bintro()
            yfn.update_headers(news_symbol)
            yfn.form_url_endpoint(news_symbol)
            yfn.do_simple_get()
            uh = url_hinter(1, args)        # anyone needs to be able to get hints on a URL from anywhere
            yfn.share_hinter(uh)
            yfn.scan_news_feed(news_symbol, 0, 0)       # (params) #1: level, #2: 0=HTML / 1=JavaScript
            yfn.eval_article_tags(news_symbol)          # ml_ingest{} is built
            print ( f" " )
            print ( "========================= Evaluate quality of ML/NLP candidates =========================" )

            nlp_summary()
            print ( f" " )
            
        return