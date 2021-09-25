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
from shallow_logic import shallow_combo
from ml_cvbow import y_bow
from bigcharts_md import bc_quote
from marketwatch_md import mw_quote
from ml_yahoofinews import yfnews_reader
from ml_urlhinter import url_hinter

#from y_newsloop import y_newsfilter

# Globals
work_inst = 0
global args
args = {}
global parser
parser = argparse.ArgumentParser(description="Entropy apperture engine")
parser.add_argument('-c','--cycle', help='Ephemerial top 10 every 10 secs for 60 secs', action='store_true', dest='bool_tenten60', required=False, default=False)
parser.add_argument('-d','--deep', help='Deep converged multi data list', action='store_true', dest='bool_deep', required=False, default=False)
parser.add_argument('-a','--allnews', help='ML/NLP News sentiment AI for all stocks', action='store_true', dest='bool_news', required=False, default=False)
parser.add_argument('-n','--newsai', help='ML/NLP News sentiment AI for 1 stock', action='store', dest='newsymbol', required=False, default=False)
parser.add_argument('-q','--quote', help='Get ticker price action quote', action='store', dest='qsymbol', required=False, default=False)
parser.add_argument('-s','--screen', help='Small cap screener logic', action='store_true', dest='bool_scr', required=False, default=False)
parser.add_argument('-t','--tops', help='show top ganers/losers', action='store_true', dest='bool_tops', required=False, default=False)
parser.add_argument('-u','--unusual', help='unusual up & down volume', action='store_true', dest='bool_uvol', required=False, default=False)
parser.add_argument('-v','--verbose', help='verbose error logging', action='store_true', dest='bool_verbose', required=False, default=False)
parser.add_argument('-x','--xray', help='dump detailed debug data structures', action='store_true', dest='bool_xray', required=False, default=False)

# Threading globals
extract_done = threading.Event()
yti = 1
uh = url_hinter(1, args)

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
        topg_inst.get_topg_data()        # extract data from finance.Yahoo.com
        topg_inst.build_tg_df0()
        topg_inst.build_top10()
        topg_inst.build_tenten60(r)     # pass along current cycle
        print ( ".", end="", flush=True )
        topg_inst.cycle += 1    # adv loop cycle

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


#######################################################################
# TODO: methods/Functions to add...
#       see README and TODO.txt

############################# main() ##################################
#

def main():
    cmi_debug = __name__+"::".__init__.__name__
    global args
    args = vars(parser.parse_args())        # args as a dict []

    print ( " " )
    print ( "########## Initalizing ##########" )
    print ( " " )

    print ( "CMDLine args:", parser.parse_args() )
    logging.info ( f"%s - url-hinter engine started: {type(uh)}" % cmi_debug )
    uh.hstatus()
    # ARGS[] cmdline pre-processing
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
        print ( "========== Top 10 Gainers ==========" )
        print ( " " )
        med_large_mega_gainers = y_topgainers(1)       # instantiate class
        med_large_mega_gainers.get_topg_data()        # extract data from finance.Yahoo.com
        x = med_large_mega_gainers.build_tg_df0()     # build full dataframe
        med_large_mega_gainers.build_top10()           # show top 10
        med_large_mega_gainers.print_top10()           # print it
        print ( " " )

########### 2 - TOP LOSERS ################
    if args['bool_tops'] is True:
        print ( "========== Top 10 Losers ==========" )
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

# generate INITIAL combo list ######################################################
    """
    DEEP amalysis means - try to understand & inferr plain language reasons as to why these stock are
    appearing in the final 'Single Source of Truth' combo_df. Having a big list of top mover/highly active
    stocks isn't meaningful unless you can understand (quickly in real-time) whats going on with each one.
    From that pint, you can plan to do something... otherwise, this is just a meaningless list.
    NOTE: Raw Data is never usable in its initial state. It allways has holes, is dirty & needs wrangeling.
          Much of this code prepares & cleans the data into a perfect combo_df 'Single Source of Truth'.
    """

    if args['bool_deep'] is True and args['bool_scr'] is True and args['bool_uvol'] is True:

        # FIRST, merge Small_cap + med + large + mega into a single DF
        x = shallow_combo(1, med_large_mega_gainers, small_cap_dataset, un_vol_activity, args )
        x.prepare_combo_df()
        # Find/fix missing data in nasdaq.com unusual volume DF - i.e. market_cap info
        uvol_badata = x.combo_df[x.combo_df['Mkt_cap'].isna()]
        up_symbols = uvol_badata['Symbol'].tolist()
        nq = nquote(3, args)                   # setup an emphemerial dict
        nq.init_dummy_session()                # setup request session - note: will set nasdaq magic cookie
        total_wrangle_errors = 0               # usefull counters
        unfixable_errors = 0
        cleansed_errors = 0
        logging.info('main::x.combo - find missing data for: %s symbols' % len(up_symbols) )
        loop_count = 1

        for qsymbol in up_symbols:             # iterate over symbols & get a live quote for each one
            xsymbol = qsymbol                  # raw field from df to match df insert column test - sloppy hack, it has trailing spaces
            qsymbol = qsymbol.rstrip()         # same data but cleand/striped of trailing spaces
            logging.info( f"main::x.combo ================ get quote: {qsymbol} : %s ====================" % loop_count )
            nq.update_headers(qsymbol)         # set path: header object. doesnt touch secret nasdaq cookies
            nq.form_api_endpoint(qsymbol)      # set API endpoint url
            nq.get_nquote(qsymbol)             # get a live quote
            wrangle_errors = nq.build_data()   # wrangle & cleanse the data - lots done in here
            print ( f"symbol: {qsymbol} ", end="", flush=True )

            if wrangle_errors == -1:           # bad symbol (not a regular stock)
                logging.info( f"main::x.combo - {qsymbol} bad / not regular ticker: %s" % qsymbol )
                nq.quote.clear()               # make sure ephemerial quote{} is always empty before bailing out
                wrangle_errors = 1
                unfixable_errors += 1
                print ( f"- UNFIXABLE data problem / Not regular stock / ETF Trust: EF / Data issues: {wrangle_errors}" )
                # set default data for non-regualr stocks
                x.combo_df.at[x.combo_df[x.combo_df['Symbol'] == xsymbol].index, 'Mkt_cap'] = round(float(0), 3)
                x.combo_df.at[x.combo_df[x.combo_df['Symbol'] == xsymbol].index, 'M_B'] = 'EF'
            elif nq.quote['mkt_cap'] != 0:            # catch zero mkt cap
                # insert missing data into dataframe @ row / column
                print ( f"- INSERT missing data / Market cap: {nq.quote['mkt_cap']} ", end='', flush=True )
                x.combo_df.at[x.combo_df[x.combo_df['Symbol'] == xsymbol].index, 'Mkt_cap'] = nq.quote['mkt_cap']
                cleansed_errors += 1
                # compute market cap scale indicator (Small/Large Millions/Billions/Trillions)
                for i in (("MT", 999999), ("LB", 10000), ("SB", 2000), ("LM", 500), ("SM", 50), ("TM", 10), ("UZ", 0)):
                    if i[1] >= nq.quote['mkt_cap']:
                        pass
                    else:
                        wrangle_errors += 1          # insert market cap scale into DF @ column M_B for this symbol
                        x.combo_df.at[x.combo_df[x.combo_df['Symbol'] == xsymbol].index, 'M_B'] = i[0]
                        print ( f"/ Mkt cap scale: {i[0]} - Data issues: {wrangle_errors}" )
                        logging.info( "main::x.combo - Computed Market cap scale as %s / DF updated!" % i[0] )
                        cleansed_errors += 1
                        break
            else:
                wrangle_errors += 2     # regular symbol with ZERO ($0) market cap is a bad data error
                print ( f"- INSERT missing data / Market cap: 0 / Mkt cap scale: UZ - Data issues: {wrangle_errors}" )
                x.combo_df.at[x.combo_df[x.combo_df['Symbol'] == xsymbol].index, 'M_B'] = "UZ"
                x.combo_df.at[x.combo_df[x.combo_df['Symbol'] == xsymbol].index, 'Mkt_cap'] = float(0)
                cleansed_errors += 1

            logging.info( f"main::x.combo ================ end quote: {qsymbol} : %s ====================" % loop_count )
            total_wrangle_errors = total_wrangle_errors + wrangle_errors
            wrangle_errors = 0
            loop_count += 1
        print ( " " )
        print  ( f"Symbols scanned: {loop_count-1} / Issues: {cleansed_errors} / Repaired: {total_wrangle_errors} / Unfixbale: {unfixable_errors}" )

# generate FINAL combo list ################################################################################
# combine all the findings into 1 place - single source of truth

        print ( " " )
        print ( f"================= >>COMBO<< Full list of intersting market observations ==================" )
        x.tag_dupes()
        x.tag_uniques()
        x.rank_hot()
        x.rank_unvol()
        x.rank_caps()
        x.combo_listall_ranked()

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
        print ( averages )
        print ( " " )
        print ( f"Current day average $ gain: ${averages.iloc[-1]['Prc_change'].round(2)}" )
        print ( f"Current day percent gain:   %{averages.iloc[-1]['Pct_change'].round(2)}" )

# Machine Learning NLP (Natural Language Processing) ####################################
# News Sentiment AI
    #def confidence_ind(r_uhint, tc, ru, su):
    def confidence_ind(r_uhint, r_thint, r_xturl, orig_url):
        """
        NLP Support function #1
        r_uhint = locality confidence code (0=remote, 1=local, 9=ERROR_bad_page_struct, 10=ERROR_unknown_state)
        tc = type confidence code (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        ru = Real remote url (extracted)
        su = Fake url from Depth 0 news feed
        Print some nicely formatted info about this discovered article
        NOTE: Locality codes are inferred by decoding the page HTML structure
              They do not match/align with the URL Hint code. Since that could be a 'fake out'
        """
        cmi_debug = __name__+"::confidence_ind().#1    "
        tcode = { 0.0: 'Real news - local page',
                1.0: 'Real news - remote-stub',
                1.1: 'Real news - remote-abs',
                2.0: 'OP-Ed - local',
                2.1: 'OP-Ed - remote',
                3.0: 'Curated report - local',
                3.1: 'Curated report - remote',
                4.0: 'Video story - local',
                4.1: 'Video story - remote',
                5.0: 'Micro-ad - local',
                5.1: 'Micro-ad - remote',
                6.0: 'Bulk ad - local',
                6.0: 'Bulk ad - remote',
                7.0: 'Unknown thint 7.0',
                8.0: 'Unknown thint 8.0',
                9.0: 'Unknown thing 9.0',
                9.9: 'Unknown page structure',
                10.0: 'ERROR unknonw state',
                99.9: 'DEfault NO-YET-SET'
                }
        logging.info ( f"%s - hint code recieved: {r_thint}" % cmi_debug )
        thint_descr = tcode.get(r_thint)
        print ( f"Confidence:    u:{r_uhint} / h:{r_thint} {thint_descr}" )
        print ( f"News feed URL: {orig_url}" )
        print ( f"Real dest URL: {r_xturl}" )
        return


    def nlp_final_prep():
        """
        NLP Support function #3
        Assumes ml_ingest is allreay pre-built
        process all target items in ml_ingest{} i.e. candidate NLP news articles
        figure out which ones to commit to NLP READ
        AWRN: even at this level of depth (2), where we've built up good confidence of which articles to read....
              we can still be fooled by deceptive/fake articles inserted in the news feed & odd article structures...
              especially Micro Adds & curated articles inserted in the news feed. (there are many artcile types)
              Also, false positive articles that may-not have any news relating to this symbol. (News agency's are sleazy!).
        """
        print ( " ")
        print ( f"====================== Depth 2 ======================" )
        cmi_debug = __name__+"::nlp_final_prep().#1    "
        for sn_idx, sn_row in yfn.ml_ingest.items():    # cycle thru the NLP candidate list
            if sn_row['type'] == 0:                       # REAL news, inferred from Depth 0
                print( f"News article:  {sn_idx} / ", end="" )
                t_url = urlparse(sn_row['url'])           # WARN: a rlparse() url_named_tupple (NOT the raw url)
                uhint, uhdescr = uh.uhinter(1, t_url)
                thint = (sn_row['thint'])                  # the hint we guessed at while interrogating page <tags>
                logging.info ( f"%s - #1 get_locality hints: t:0 / u:{uhint} / h: {thint} {uhdescr}" % cmi_debug )
                r_uhint, r_thint, r_xturl = yfn.get_locality(sn_idx, sn_row)    # go deep, with everything we knonw about this item
                print ( f"#0 {uhdescr} - NLP candidate" )                       # all type 0 are assumed to be REAL news
                confidence_ind(r_uhint, r_thint, r_xturl, sn_row['url'] )       # dodes NOT chnage any data, just nice output
                print ( f"====================== Depth 2 ======================" )
                #
            elif sn_row['type'] == 1:                     # possibly not news? (Micro Ad)
                print( f"News article:  {sn_idx} / ", end="" )
                t_url = urlparse(sn_row['url'])
                uhint, uhdescr = uh.uhinter(2, t_url)
                thint = (sn_row['thint'])                 # the hint we guess at while interrogating page <tags>
                logging.info ( f"%s - #2 get_locality hints: t:1 / u:{uhint} / h: {thint} {uhdescr}" % cmi_debug )
                r_uhint, r_thint, r_xturl = yfn.get_locality(sn_idx, sn_row)    # go deep, with everything we knonw about this item
                print ( f"#1 {uhdescr} - NLP candidate" )                       # all type 1 are only possible news
                confidence_ind(r_uhint, r_thint, r_xturl, sn_row['url'] )       # dodes NOT chnage any data, just nice output
                print ( f"====================== Depth 2 ======================" )
                #
            elif sn_row['type'] == 2:                     # possibly not news? (Micro Ad)
                print ( f"Bulk injected ad NOT an NLP candidate" )
                logging.info ( f"%s - #3 skipping..." % cmi_debug )
                print ( f"====================== Depth 2 ======================" )
                #
            else:
                print ( f"ERROR unknown article type in ml_ingest" )
                logging.info ( f"%s - #4 skipping..." % cmi_debug )
                print ( f"====================== Depth 2 ======================" )

        return

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
        #news_symbol = str(args['newsymbol'])       # symbol provided on CMDLine
        yfn = yfnews_reader(1, "IBM", args )        # dummy symbol just for instantiation
        yfn.init_dummy_session()
        uh.hstatus()
        yfn.share_hinter(uh)                        # share the url hinter available
        #yfn.yfn_bintro()
        print ( "============================== Prepare bulk NLP candidate list =================================" )
        print ( f"ML/NLP candidates: {newsai_test_dataset.tg_df1['Symbol'].tolist()}" )
        for nlp_target in newsai_test_dataset.tg_df1['Symbol'].tolist():
            yfn.update_headers(nlp_target)
            yfn.form_url_endpoint(nlp_target)
            yfn.do_simple_get()
            yfn.scan_news_feed(nlp_target, 0, 0)    # (params) #1: level, #2: 0=HTML / 1=JavaScript
            yfn.eval_article_tags(nlp_target)       # ml_ingest{} is built
            print ( "============================== NLP candidates are ready =================================" )

        #yfn.dump_ml_ingest()
        # nlp_final_prep(uh)

# Read the news for just 1 stock symbol
    """
    The machine will read now!
    Read finance.yahoo.com / News 'Brief headlines' (i.e. short text docs) for ONE stock symbol.
    """
    if args['newsymbol'] is not False:
        cmi_debug = __name__+"::nlp_one.#1"
        print ( " " )
        print ( "========================= ML (NLP) / Yahoo Finance News Sentiment AI =========================" )
        print ( f"Examine & Read news for 1 stock symbol..." )
        news_symbol = str(args['newsymbol'])       # symbol provided on CMDLine
        yfn = yfnews_reader(1, news_symbol, args )   # dummy symbol just for instantiation
        yfn.init_dummy_session()
        #yfn.yfn_bintro()
        yfn.update_headers(news_symbol)
        yfn.form_url_endpoint(news_symbol)
        yfn.do_simple_get()
        logging.info ( f"%s - Enable url hinter-engine: {type(uh)}" % cmi_debug )
        uh.hstatus()
        yfn.share_hinter(uh)
        yfn.scan_news_feed(news_symbol, 0, 0)    # (params) #1: level, #2: 0=HTML / 1=JavaScript
        yfn.eval_article_tags(news_symbol)          # ml_ingest{} is built

        print ( f" " )
        print ( "========================= Evaluate quality of ML/NLP candidates =========================" )
        nlp_final_prep()

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
        nq = nquote(4, args)                         # setup an emphemerial dict
        nq.init_dummy_session()                      # note: this will set nasdaq magic cookie
        nq_symbol = args['qsymbol'].upper()
        logging.info('main::simple get_quote - for symbol: %s' % nq_symbol )
        nq.update_headers(nq_symbol.rstrip())        # set path: header. doesnt touch secret nasdaq cookies
        nq.form_api_endpoint(nq_symbol.rstrip())
        nq.get_nquote(nq_symbol.rstrip())
        wrangle_errors = nq.build_data()             # return num of data wrangeling errors we found & dealt with
        nq.build_df()
        print ( " " )
        print ( f"Get Nasdaq.com quote for: {nq_symbol}" )
        #print ( f"================= quote json =======================" )
        if nq.quote.get("symbol") is not None:
            #print ( f"{nq.quote}" )                # >>DEBUG<< dump the quote dict{}
            #print ( f"{nq.quote_df0}" )            # >>DEBUG<< dump the dataframe
            print ( f"================= Nasdaq quote data =======================" )
            c = 1
            for k, v in nq.quote.items():
                print ( f"{c} - {k} : {v}" )
                c += 1
            print ( f"===============================================================" )
            print ( " " )
        else:
            print ( f"Not a regular symbol - prob Trust, ETF etc" )

    """
    EXAMPLE #2
    bigcharts.marketwatch.com - data via BS4 scraping
    quote price data is 15 mins delayed
    10 data fields provided
    """
    if args['qsymbol'] is not False:
        bc = bc_quote(5, args)       # setup an emphemerial dict
        bc_symbol = args['qsymbol'].upper()  # what symbol are we getting a quote for?
        bc.get_basicquote(bc_symbol) # get the quote
        print ( " " )
        print ( f"Get BIGCharts.com BasicQuote for: {bc_symbol}" )
        #print ( f"================= quote json =======================" )
        #print ( f"{bc.quote}" )    # >>DEBUG<< dump the quote dict{}
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
        bc = bc_quote(5, args)       # setup an emphemerial dict
        bc_symbol = args['qsymbol'].upper()  # what symbol are we getting a quote for?
        bc.get_quickquote(bc_symbol) # get the quote
        bc.q_polish()                # wrangel the data elements
        print ( " " )
        print ( f"Get BIGCharts.com QuickQuote for: {bc_symbol}" )
        #print ( f"================= quickquote json =======================" )
        #print ( f"{bc.quote}" )     # >>DEBUG<< dump the quote dict{}
        print ( f"================= quickquote data =======================" )
        c = 1
        for k, v in bc.quote.items():
            print ( f"{c} - {k} : {v}" )
            c += 1
        print ( f"========================================================" )
        print ( " " )


if __name__ == '__main__':
    cmi_debug = __name__+"::".__init__.__name__
    main()
