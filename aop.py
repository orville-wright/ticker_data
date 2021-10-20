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
import random
from urllib.parse import urlparse
from rich import print

# ML capabilities
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords

# logging setup
logging.basicConfig(level=logging.INFO)

# my private classes & methods
from y_topgainers import y_topgainers
from y_toplosers import y_toplosers
from screener_dg1 import screener_dg1
from nasdaq_uvoljs import un_volumes
from nasdaq_quotes import nquote
from shallow_logic import combo_logic
from ml_cvbow import y_bow
from bigcharts_md import bc_quote
from marketwatch_md import mw_quote
from ml_yahoofinews import yfnews_reader
from ml_urlhinter import url_hinter
from y_techevents import y_techevents

# Globals
work_inst = 0
global args
args = {}
global parser
parser = argparse.ArgumentParser(description="Entropy apperture engine")
parser.add_argument('-a','--allnews', help='ML/NLP News sentiment AI for all stocks', action='store_true', dest='bool_news', required=False, default=False)
parser.add_argument('-c','--cycle', help='Ephemerial top 10 every 10 secs for 60 secs', action='store_true', dest='bool_tenten60', required=False, default=False)
parser.add_argument('-d','--deep', help='Deep converged multi data list', action='store_true', dest='bool_deep', required=False, default=False)
parser.add_argument('-n','--newsai', help='ML/NLP News sentiment AI for 1 stock', action='store', dest='newsymbol', required=False, default=False)
parser.add_argument('-p','--perf', help='Tech event performance sentiment', action='store_true', dest='bool_te', required=False, default=False)
parser.add_argument('-q','--quote', help='Get ticker price action quote', action='store', dest='qsymbol', required=False, default=False)
parser.add_argument('-s','--screen', help='Small cap screener logic', action='store_true', dest='bool_scr', required=False, default=False)
parser.add_argument('-t','--tops', help='show top ganers/losers', action='store_true', dest='bool_tops', required=False, default=False)
parser.add_argument('-u','--unusual', help='unusual up & down volume', action='store_true', dest='bool_uvol', required=False, default=False)
parser.add_argument('-v','--verbose', help='verbose error logging', action='store_true', dest='bool_verbose', required=False, default=False)
parser.add_argument('-x','--xray', help='dump detailed debug data structures', action='store_true', dest='bool_xray', required=False, default=False)

# Threading globals
extract_done = threading.Event()
yti = 1
#uh = url_hinter(1, args)        # anyone needs to be able to get hints on a URL from anywhere

#######################################################################
# Global method for __main__
# thread function #1
# DEPRECATED

def do_nice_wait(topg_inst):
    """Threaded wait that does work to build out the 10x10x60 DataFrame"""
    logging.info('y_topgainers:: IN Thread - do_nice_wait()' )
    logging.info('y_topgainers::do_nice_wait() -> inst: %s' % topg_inst.yti )
    for r in range(6):
        logging.info('do_nice_wait() cycle: %s' % topg_inst.cycle )
        time.sleep(5)    # wait immediatley to let remote update
        topg_inst.get_topg_data()       # extract data from finance.Yahoo.com
        topg_inst.build_tg_df0()
        topg_inst.build_top10()
        topg_inst.build_tenten60(r)     # pass along current cycle
        print ( ".", end="", flush=True )
        topg_inst.cycle += 1            # adv loop cycle

        if topg_inst.cycle == 6:
            logging.info('do_nice_wait() - EMIT exit trigger' )
            extract_done.set()

    logging.info('do_nice_wait() - Cycle: %s' % topg_inst.cycle )
    logging.info('do_nice_wait() - EXIT thread inst: %s' % topg_inst.yti )

    return      # dont know if this this requireed or good semantics?

def bkgrnd_worker():
    """Threaded wait that does work to build out the 10x10x60 DataFrame"""
    global work_inst
    logging.info('main::bkgrnd_worker() IN Thread - bkgrnd_worker()' )
    logging.info('main::bkgrnd_worker() Ref -> inst #: %s' % work_inst.yti )
    for r in range(4):
        logging.info('main::bkgrnd_worker():: Loop: %s' % r )
        time.sleep(30)    # wait immediatley to let remote update
        work_inst.get_topg_data()        # extract data from finance.Yahoo.com
        work_inst.build_tg_df0()
        work_inst.build_top10()
        work_inst.build_tenten60(r)

    logging.info('main::bkgrnd_worker() EMIT exit trigger' )
    extract_done.set()
    logging.info('main::bkgrnd_worker() EXIT thread inst #: %s' % work_inst.yti )
    return      # dont know if this this requireed or good semantics?


############################# main() ##################################

def main():
    cmi_debug = "aop::"+__name__+"::main()"
    global args
    args = vars(parser.parse_args())        # args as a dict []
    print ( " " )
    print ( "########## Initalizing ##########" )
    print ( " " )
    print ( "CMDLine args:", parser.parse_args() )
    if args['bool_verbose'] is True:        # Logging level
        print ( "Enabeling verbose info logging..." )
        logging.disable(0)                  # Log level = OFF
    else:
        logging.disable(20)                 # Log lvel = INFO

    if args['newsymbol'] is not False:
        print ( " " )
        print ( f"Scanning news for symbol: {args['newsymbol']}" )

    print ( " " )

    recommended = {}        # dict of recomendations

########### 1 - TOP GAINERS ################
    if args['bool_tops'] is True:
        print ( "========== Top Gainers / Large Cap ==========" )
        print ( " " )
        med_large_mega_gainers = y_topgainers(1)       # instantiate class
        med_large_mega_gainers.get_topg_data()        # extract data from finance.Yahoo.com
        x = med_large_mega_gainers.build_tg_df0()     # build full dataframe
        med_large_mega_gainers.build_top10()           # show top 10
        med_large_mega_gainers.print_top10()           # print it
        print ( " " )

########### 2 - TOP LOSERS ################
    if args['bool_tops'] is True:
        print ( "========== Top Losers / Large Cap ==========" )
        print ( " ")
        med_large_mega_loosers = y_toplosers(1)       # instantiate class
        med_large_mega_loosers.get_topg_data()        # extract data from finance.Yahoo.com
        x = med_large_mega_loosers.build_tg_df0()     # build full dataframe
        med_large_mega_loosers.build_top10()           # show top 10
        med_large_mega_loosers.print_top10()           # print it
        print ( " ")

########### 3 10x10x60 ################
# **THREAD** waiter
    # do 10x10x60 build-out cycle
    # currently fails to produce a unique data set each threat cycle. Don't know why
    if args['bool_tenten60'] is True:
        print ( "Doing 10x10x60 Gainers loop cycle" )
        logging.info('main() - Doing 10x10x60 thread cycle' )
        global work_inst
        work_inst = y_topgainers(2)
        thread = threading.Thread(target=bkgrnd_worker)    # thread target passes class instance
        logging.info('main() - START thread #1 > 10x10x60 cycler' )
        print ( "Thread loop cycle: ", end="" )
        thread.start()
        while not extract_done.wait(timeout=5):     # wait on thread completd trigger
            print ( ".", end="", flush=True )

        print ( " " )
        # print ( work_inst.tg_df2.sort_values(by=['Symbol','Time'], ascending=True ) )
        print ( work_inst.tg_df2.sort_values(by=['ERank','Time'] ) )

    else:
        print ( " " )

########### Small Cap gainers & loosers ################
# small caps are isolated outside the regular dataset by yahoo.com
    if args['bool_scr'] is True:
        print ( "========== Screener: SMALL CAP Day Gainers : +5% & > $299M Mkt-cap ==========" )
        small_cap_dataset = screener_dg1(1)       # instantiate class
        small_cap_dataset.get_data()              # extract data from finance.Yahoo.com
        x = small_cap_dataset.build_df0()         # build full dataframe
        # scrn1.build_top10()           # show top 10
        # scrn1.print_top10()           # print it

        # Recommendation #1 - Best small cap % gainer with lowest buy-in price
        recommended.update(small_cap_dataset.screener_logic())
        print ( " ")

# process Nasdaq.com unusual_vol ################
    if args['bool_uvol'] is True:
        print ( "========== Unusually high Volume ** UP ** =====================================================" )
        un_vol_activity = un_volumes(1, args)       # instantiate NEW nasdaq data class, args = global var
        un_vol_activity.get_un_vol_data()           # extract JSON data (Up & DOWN) from api.nasdaq.com

        # should test success of extract before attempting DF population
        un_vol_activity.build_df(0)           # 0 = UP Unusual volume
        un_vol_activity.build_df(1)           # 1 = DOWN unusual volume

        # find lowest price stock in unusuall UP volume list
        up_unvols = un_vol_activity.up_unvol_listall()      # temp DF, nicely ordered & indexed of unusual UP vol activity
        ulp = up_unvols['Cur_price'].min()                  # find lowest price row in DF
        uminv = up_unvols['Cur_price'].idxmin()             # get index ID of lowest price row
        ulsym = up_unvols.loc[uminv, ['Symbol']][0]         # get symbol of lowest price item @ index_id
        ulname = up_unvols.loc[uminv, ['Co_name']][0]       # get name of lowest price item @ index_id
        upct = up_unvols.loc[uminv, ['Pct_change']][0]      # get %change of lowest price item @ index_id
        print ( f">>LOWEST<< buy price OPPTY is: #{uminv} - {ulname.rstrip()} ({ulsym.rstrip()}) @ ${ulp} / {upct}% gain" )
        print ( " " )
        print ( f"{un_vol_activity.up_unvol_listall()} " )
        print ( " ")
        print ( "========== Unusually high Volume ** DOWN ** =====================================================" )
        print ( f"{un_vol_activity.down_unvol_listall()} " )
        print ( " ")
        # Add unusual vol into recommendations list []
        #recommended['2'] = ('Unusual vol:', ulsym.rstrip(), '$'+str(ulp), ulname.rstrip(), '+%'+str(un_vol_activity.up_df0.loc[uminv, ['Pct_change']][0]) )
        recommended['2'] = ('Unusual vol:', ulsym.rstrip(), '$'+str(ulp), ulname.rstrip(), '+%'+str(upct) )

# generate FINAL combo list ################################################################################
# combine all the findings into 1 place - single source of truth
    """
    DEEP amalysis means - try to understand & inferr plain language reasons as to why these stock are
    appearing in the final 'Single Source of Truth' combo_df. Having a big list of top mover/highly active
    stocks isn't meaningful unless you can understand (quickly in real-time) whats going on with each one.
    From here, you can plan to do something... otherwise, this is just a meaningless list.
    NOTE: Most of this logic prepares/cleans/wrangles data into a perfect combo_df 'Single Source of Truth'.
    """
    if args['bool_deep'] is True and args['bool_scr'] is True and args['bool_uvol'] is True:
        x = combo_logic(1, med_large_mega_gainers, small_cap_dataset, un_vol_activity, args )
        x.polish_combo_df(1)
        print ( " " )
        print ( f"================= >>COMBO<< Full list of intersting market observations ==================" )
        x.tag_dupes()
        x.tag_uniques()
        x.rank_hot()
        x.rank_unvol()
        x.rank_caps()
        print ( f"{x.combo_listall_ranked()}" )


# Summarize combo list key findings ##################################################################
        # Curious Outliers
        temp_1 = x.combo_df.sort_values(by=['Pct_change'], ascending=False)
        print ( " " )
        print ( "========== ** OUTLIERS ** : Unusual UP volume + Top Gainers by +5% ================================" )
        print ( " " )
        print ( f"{temp_1[temp_1.duplicated(['Symbol'])]}" )    # duples in the df mean a curious outlier

        if len(x.rx) == 0:      # # hottest stock with lowest price overall
            print ( " " )       # empty list[] = no stock found yet (prob very early in trading morning)
            print ( f"No **hot** stock for >>LOW<< buy-in recommendations list yet" )
        else:
            hotidx = x.rx[0]
            hotsym = x.rx[1]
            hotp = x.combo_df.loc[hotidx, ['Cur_price']][0]
            hotname = x.combo_df.loc[hotidx, ['Co_name']][0]
            print ( " " )       # empty list[] = no stock found yet (prob very early in trading morning)
            recommended['3'] = ('Hottest:', hotsym.rstrip(), '$'+str(hotp), hotname.rstrip(), '+%'+str(x.combo_df.loc[hotidx, ['Pct_change']][0]) )
            print ( f">>Lowest price<< **Hot** stock: {hotsym.rstrip()} - {hotname.rstrip()} / {'$'+str(hotp)} / {'+%'+str(x.combo_df.loc[hotidx, ['Pct_change']][0])} gain" )
            print ( " " )
            print ( " " )

        # lowest priced stock
        clp = x.combo_df['Cur_price'].min()
        cminv = x.combo_df['Cur_price'].idxmin()
        clsym = x.combo_df.loc[cminv, ['Symbol']][0]
        clname = x.combo_df.loc[cminv, ['Co_name']][0]
        recommended['4'] = ('Large cap:', clsym.rstrip(), '$'+str(clp), clname.rstrip(), '+%'+str(x.combo_df.loc[cminv, ['Pct_change']][0]) )

        # Biggest % gainer stock
        cmax = x.combo_df['Pct_change'].idxmax()
        clp = x.combo_df.loc[cmax, 'Cur_price']
        clsym = x.combo_df.loc[cmax, ['Symbol']][0]
        clname = x.combo_df.loc[cmax, ['Co_name']][0]
        recommended['5'] = ('Top % gainer:', clsym.rstrip(), '$'+str(clp), clname.rstrip(), '+%'+str(x.combo_df.loc[cmax, ['Pct_change']][0]) )

# Recommendeds ###############################################################
        #  key    recomendation data     - (example output shown)
        # =====================================================================
        #   1:    Small cap % gainer: TXMD $0.818 TherapeuticsMD, Inc. +%7.12
        #   2:    Unusual vol: SPRT $11.17 support.com, Inc. +%26.79
        #   3:    Hottest: AUPH $17.93 Aurinia Pharmaceuticals I +%9.06
        #   4:    Large cap: PHJMF $0.07 PT Hanjaya Mandala Sampoe +%9.2
        #   5:    Top % gainer: SPRT $19.7 support.com, Inc. +%41.12
        # todo: we should do a linear regression on the price curve for each item

        print ( " " )
        print ( f"============ recommendations >>Lowest buy price<< stocks with greatest % gain  =============" )
        print ( " " )
        for k, v in recommended.items():
            print ( f"{k:3}: {v[0]:21} {v[1]:6} {v[3]:28} {v[2]:8} /  {v[4]}" )
            print ( "--------------------------------------------------------------------------------------------" )

# Summary ############### AVERGAES and computed info ##########################
        print ( " " )
        print ( "============== Market activity overview, inisghts & stats =================" )
        averages = x.combo_grouped().round(2)       # insights
        print ( " " )
        print ( f"{averages}" )
        print ( " " )
        print ( f"Current day average $ gain: ${averages.iloc[-1]['Prc_change'].round(2)}" )
        print ( f"Current day percent gain:   %{averages.iloc[-1]['Pct_change'].round(2)}" )



# Get the TSML performance Sentiment for all stocks in combo DF ######################
    if args['bool_te'] is True:
        cmi_debug = __name__+"::Tech_events_all.#1"
        te_targets = x.list_uniques()
        cols = 1
        te = y_techevents(3)
        print ( f"\n===== Build Tech Events performance Sentiment ==============================" )
        for xte in te_targets['Symbol'].tolist():
            nq_symbol = xte.strip().upper()
            print ( f"{xte}...", end="" )
            te.form_api_endpoints(nq_symbol)
            te_status = te.get_te_zones(1)
            if te_status != 0:              # FAIL : cant get te_zone data
                te.te_is_bad()              # FAIL : build FAILURE dict
                te.build_te_df(1)           # FAIL: insert failure status into DataFrame for this symbol
                print ( f"!", end="" )
                logging.info( f"{cmi_debug} - FAILED to get Tech Event data: Clear all dicts" )
                te.te_sentiment.clear()
            else:
                print ( f"+", end="" )     # GOOD : suceeded to get TE indicators
                te.build_te_data(1)
                te.build_te_df(2)
            cols += 1
            if cols == 8:
                print ( f" " )  # onlhy print 8 symbols per row
                cols = 1
            else:
                print ( f" / ", end="" )
            te.te_sentiment.clear()

        te.reset_te_df0()
        print ( f"\n===== Tech Events performance Sentiment ==============================" )
        #print ( f"{te.te_df0}" )
        #mask = {'Today': ['Bullish'], 'Short': ['Bullish'], 'Mid': ['Bullish'], 'Long': ['Bullish']}
        #print ( f"{te.te_df0.isin(mask)}" )
        hot_result = te.te_df0[te.te_df0['Today', 'Short', 'Mid', 'Long'] == 'Bullish']
        print ( f"{hot_result}" )
    else:
        pass



# ML / NLP section #############################################################

    def nlp_summary():
        """
        NLP Support function #3
        Assumes ml_ingest is already pre-built
        Cycles thru each item in the ml_ingest{} and processes...
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

# Read the news for multiple stock symbols
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

# Read the news for just 1 stock symbol
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



#################################################################################
# 3 differnt methods to get a live quote ########################################
# NOTE: These 3 routines are *examples* of how to get quotes from the 3 live quote classes::
# TODO: Add a 4th method - via alpaca live API

    """
    EXAMPLE: #1
    nasdaq.com - live quotes via native JSON API test GET
    quote price data is 5 mins delayed
    10 data fields provided
    """
    if args['qsymbol'] is not False:
        nq = nquote(4, args)                         # NAsdaq quote instance
        nq.init_dummy_session()                      # note: this will set nasdaq magic cookie
        nq_symbol = args['qsymbol'].upper()
        logging.info( f"%s - Get Nasdaq.com quote for symbol {nq_symbol}" % cmi_debug )
        nq.update_headers(nq_symbol, "stocks")         # set path: header object. doesnt touch secret nasdaq cookies
        nq.form_api_endpoint(nq_symbol, "stocks")      # set API endpoint url - default GUESS asset_class=stocks
        #
        ac = nq.learn_aclass(nq_symbol)
        #
        if ac != "stocks":
            logging.info( f"%s - re-shape asset class endpoint to: {ac}" % cmi_debug )
            nq.form_api_endpoint(nq_symbol, ac)      # re-form API endpoint if default asset_class guess was wrong)
        nq.get_nquote(nq_symbol.rstrip())
        wrangle_errors = nq.build_data()             # return num of data wrangeling errors we found & dealt with
        nq.build_df()
        #
        # add Tech Events Sentiment to quote dict{}
        te = y_techevents(2)
        te.form_api_endpoints(nq_symbol)
        success = te.get_te_zones(2)
        if success == 0:
            te.build_te_data(2)
            te.te_into_nquote(nq)
            #nq.quote.update({"today_only": te.te_sentiment[0][2]} )
            #nq.quote.update({"short_term": te.te_sentiment[1][2]} )
            #nq.quote.update({"med_term": te.te_sentiment[2][2]} )
            #nq.quote.update({"long_term": te.te_sentiment[3][2]} )
        else:
            te.te_is_bad()      # FORCE Tech Events to be N/A
            te.te_into_nquote(nq)
        #
        print ( f"Get Nasdaq.com quote for: {nq_symbol}" )
        if nq.quote.get("symbol") is not None:
            print ( f"================= Nasdaq quote data =======================" )
            c = 1
            for k, v in nq.quote.items():
                print ( f"{c} - {k} : {v}" )
                c += 1
            print ( f"===============================================================" )
            print ( " " )
        else:
            print ( f"Not a regular symbol - prob Trust, ETF etc" )

        te.build_te_df(1)
        te.reset_te_df0()
        print ( f"===== TE DF ==========================================================" )
        print ( f"{te.te_df0}" )


    """
    EXAMPLE #2
    bigcharts.marketwatch.com - data via BS4 scraping
    quote price data is 15 mins delayed
    10 data fields provided
    """
    if args['qsymbol'] is not False:
        bc = bc_quote(5, args)                  # setup an emphemerial dict
        bc_symbol = args['qsymbol'].upper()     # what symbol are we getting a quote for?
        bc.get_basicquote(bc_symbol)            # get the quote
        print ( " " )
        print ( f"Get BIGCharts.com BasicQuote for: {bc_symbol}" )
        print ( f"================= basicquote data =======================" )
        c = 1
        for k, v in bc.quote.items():
            print ( f"{c} - {k} : {v}" )
            c += 1
        print ( f"========================================================" )
        print ( " " )

    """
    EXAMPLE #3
    bigcharts.marketwatch.com - data via BS4 scraping
    quote data is 15 mins delayed
    40 data fields provided
    """
    if args['qsymbol'] is not False:
        bc = bc_quote(5, args)                  # setup an emphemerial dict
        bc_symbol = args['qsymbol'].upper()     # what symbol are we getting a quote for?
        bc.get_quickquote(bc_symbol)            # get the quote
        bc.q_polish()                           # wrangel the data elements
        print ( " " )
        print ( f"Get BIGCharts.com QuickQuote for: {bc_symbol}" )
        print ( f"================= quickquote data =======================" )
        c = 1
        for k, v in bc.quote.items():
            print ( f"{c} - {k} : {v}" )
            c += 1
        print ( f"========================================================" )
        print ( " " )


if __name__ == '__main__':
    main()
