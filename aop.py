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
from shallow_logic import shallow_combo
from y_newsloop import y_newsfilter
from ml_cvbow import y_bow
from bigcharts_md import bc_quote
from marketwatch_md import mw_quote

# Globals
work_inst = 0
global args
args = {}
global parser
parser = argparse.ArgumentParser(description="Entropy apperture engine")
parser.add_argument('-c','--cycle', help='Ephemerial top 10 every 10 secs for 60 secs', action='store_true', dest='bool_tenten60', required=False, default=False)
parser.add_argument('-d','--deep', help='Deep converged multi data list', action='store_true', dest='bool_deep', required=False, default=False)
#parser.add_argument('-n','--newsai', help='News sentiment Ai', action='store_true', dest='bool_news', required=False, default=False)
parser.add_argument('-n','--newsai', help='News sentiment Ai', action='store', dest='newsymbol', required=False, default=False)
parser.add_argument('-q','--quote', help='Get ticker price action quote', action='store', dest='qsymbol', required=False, default=False)
parser.add_argument('-s','--screen', help='Small cap screener logic', action='store_true', dest='bool_scr', required=False, default=False)
parser.add_argument('-t','--tops', help='show top ganers/losers', action='store_true', dest='bool_tops', required=False, default=False)
parser.add_argument('-u','--unusual', help='unusual up & down volume', action='store_true', dest='bool_uvol', required=False, default=False)
parser.add_argument('-v','--verbose', help='verbose error logging', action='store_true', dest='bool_verbose', required=False, default=False)
parser.add_argument('-x','--xray', help='dump detailed debug data structures', action='store_true', dest='bool_xray', required=False, default=False)

# Threading globals
extract_done = threading.Event()
yti = 1

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
    # setup valid cmdline args
    global args
    args = vars(parser.parse_args())        # args as a dict []

    print ( " " )
    print ( "########## Initalizing ##########" )
    print ( " " )

    print ( "CMDLine args:", parser.parse_args() )
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

########### unusual_vol ################
    if args['bool_uvol'] is True:
        print ( "========== Unusually high Volume ** UP ** =====================================================" )
        un_vol_activity = un_volumes(1, args)       # instantiate NEW nasdaq data class, args = global var
        un_vol_activity.get_un_vol_data()           # extract JSON data (Up & DOWN) from api.nasdaq.com

        # should test success of extract before attempting DF population
        un_vol_activity.build_df(0)           # 0 = UP Unusual volume
        un_vol_activity.build_df(1)           # 1 = DOWN unusual volume

        # DataFrame COL NAME
        # ==================
        # Row
        # Symbol
        # Co_name
        # Cur_price
        # Prc_change
        # Pct_change
        # vol
        # vol_pct
        # Time

        # find lowest price stock in unusuall UP volume list
        ulp = un_vol_activity.up_df0['Cur_price'].min()                  # find lowest price row in DF
        uminv = un_vol_activity.up_df0['Cur_price'].idxmin()             # get index ID of lowest price row
        ulsym = un_vol_activity.up_df0.loc[uminv, ['Symbol']][0]  # get symbol of lowest price item
        ulname = un_vol_activity.up_df0.loc[uminv, ['Co_name']][0]   # get name of lowest price item
        print ( f">>LOWEST<< price OPPTY is: #{uminv} - {ulname.rstrip()} ({ulsym.rstrip()}) @ ${ulp}" )
        print ( " " )

        un_vol_activity.up_unvol_listall()
        print ( " ")
        print ( "========== Unusually high Volume ** DOWN ** =====================================================" )
        un_vol_activity.down_unvol_listall()
        print ( " ")


        # testing new method()
        #un_vol_activity.up_down_combo()

############################# build recommendation #######################################
        # recommendation list []
        #  key    recomendation data     - (example output shown)
        # =====================================================================
        #   1:    Small cap % gainer: TXMD $0.818 TherapeuticsMD, Inc. +%7.12
        #   2:    Unusual vol: SPRT $11.17 support.com, Inc. +%26.79
        #   3:    HOttest:  ??????? <broken due to shallow_combo DF collumn name changes>
        #   4:    Large cap: ??????
        #   5:    Top % gainer:  ?????

        # A list we build of a handful of recomendations
        # lowest price stock having unusually high UP volume is a good recomendation
        # todo: we should do a linear regression on the price curve for this item

        # reconemdation[2] : holds unusualaly hight volume stock with lowest buy price
        recommended['2'] = ('Unusual vol:', ulsym.rstrip(), '$'+str(ulp), ulname.rstrip(), '+%'+str(un_vol_activity.up_df0.loc[uminv, ['Pct_change']][0]) )
        recommended[uminv] = (ulsym.rstrip(), '$'+str(ulp), ulname.rstrip(), '+%'+str(un_vol_activity.up_df0.loc[uminv, ['Pct_change']][0]) )

########### multi COMBO dataframe query build-out ################
#
# This section...
# should be moved to its own class
# builds a single large DataFrame that combines all the findings into 1 place
# the combo DF will be a single source of truth to iterate over symbols and apply ML logic
# like... linear regressions for the last 5/10/15/30/60 mins
#         to decide if a stock of interest is trending UP or DOWN based on linear regressions
#         to fill out missing data fields that couldnt be grabbed during initial data gathering
#             e.g. sometimes you cant grab the symbol/price when poppulating some dataframes
#
# BROKEN: This is broken b/c the Nasdaq_Unusual volume collumn names changed

#         to fix, all the _combo_() code in shallow_combo:: class needs to be updated
#
    if args['bool_deep'] is True and args['bool_scr'] is True and args['bool_uvol'] is True:

        # first combine Small_cap + med + large + mega into a single dataframe
        x = shallow_combo(1, med_large_mega_gainers, small_cap_dataset, un_vol_activity, args )
        x.prepare_combo_df()
        print ( "========== ** OUTLIERS ** : Unusual UP volume + Top Gainers by +5% ================================" )
        print ( x.combo_dupes_only_listall(1) )
        print ( " ")
        print ( "========== ** OUTLIERS ** : Ranked by oppty price + Annotated reasons =======================================" )
        x.tag_dupes()
        x.tag_uniques()
        x.rank_hot()
        x.rank_unvol()
        x.rank_caps()

        # lowest price **Hottest** stock (i.e. hot in *all* metrics)
        if len(x.rx) == 0:      # empty list[]. no stock found yet (prob very early in trading morning)
            print ( " " )
            print ( f"No **hot** stock for >>LOW<< buy-in recommendations list yet" )
        else:
            hotidx = x.rx[0]
            hotsym = x.rx[1]
            hotp = x.combo_df.loc[hotidx, ['Cur_price']][0]
            hotname = x.combo_df.loc[hotidx, ['Co_name']][0]

            # allways make sure this is key #3 in recommendations dict
            recommended['3'] = ('Hottest:', hotsym.rstrip(), '$'+str(hotp), hotname.rstrip(), '+%'+str(x.combo_df.loc[hotidx, ['Pct_change']][0]) )
            print ( f">>LOW<< prine **Hot** stock: {hotsym.rstrip()} {'$'+str(hotp)} {hotname.rstrip()} {'+%'+str(x.combo_df.loc[hotidx, ['Pct_change']][0])} " )
            print ( " " )

        x.combo_listall_ranked()

        # lowest priced stock in combo_df
        clp = x.combo_df['Cur_price'].min()
        cminv = x.combo_df['Cur_price'].idxmin()
        clsym = x.combo_df.loc[cminv, ['Symbol']][0]
        clname = x.combo_df.loc[cminv, ['Co_name']][0]

        # allways make sure this is key #4 in recommendations dict
        recommended['4'] = ('Large cap:', clsym.rstrip(), '$'+str(clp), clname.rstrip(), '+%'+str(x.combo_df.loc[cminv, ['Pct_change']][0]) )

        # Biggest gainer stock in combo_df
        cmax = x.combo_df['Pct_change'].idxmax()
        clp = x.combo_df.loc[cmax, 'Cur_price']
        clsym = x.combo_df.loc[cmax, ['Symbol']][0]
        clname = x.combo_df.loc[cmax, ['Co_name']][0]

        # allways make sure this is key #5 in recommendations dict
        recommended['5'] = ('Top % gainer:', clsym.rstrip(), '$'+str(clp), clname.rstrip(), '+%'+str(x.combo_df.loc[cmax, ['Pct_change']][0]) )

        print ( " " )
        print ( f"================= >>LOW<< buy-in recommendations ==================" )
        for k, v in recommended.items():
            print ( f"{k}: {v[0]} {v[1]} {v[2]} {v[3]} {v[4]}" )
            print ( "-------------------------------------------------------------------" )

        print ( " " )
        print ( "============== High level activity inisghts =================" )
        averages = x.combo_grouped()       # insights
        print ( averages )
        print ( " " )

############# Machine Learning dev code ####################################
###################### News Sentiment Ai ###################################

    if args['newsymbol'] is not False:
        print ( " " )
        print ( "========== ** HACKING ** : News Sentiment Ai =======================================" )
        news_symbol = str(args['newsymbol'])            # symbol provided on CMDLine
        z = y_newsfilter(1, news_symbol, args )
        z.scan_news_depth_0()
        #z.read_allnews_depth_0()                        # if bool_deep is not set, this does shallow extraction

        if args['bool_deep'] is True:
            ml_prep = z.read_allnews_depth_0()
            news_df = pd.DataFrame.from_dict(ml_prep, orient='index', \
                        columns=['Source', 'Outet', 'url_link', 'Author', 'Age'])
            print ( " " )
            print ( news_df )
            print ( " " )
        else:
            z.read_allnews_depth_0()                        # just do a shallow extraction for ML level 1 testing

        # Machine Learning hacking
        # FOr now, focusing on New Brief headlines (i.e. short text docs)
        # print ( "---------------------------------- Source dataset ---------------------------------------------" )
        # for i in range(len(z.ml_brief)):                            # print all the News Brief headlines
        #         print ( f"News item: #{i} {z.ml_brief[i]}" )

        print ( " " )

        # ML core setup
        randnb = random.randint(0, len(z.ml_brief)-1 )  # pick a random news brief to hack/work on
        sw = stopwords.words("english")
        v = y_bow(1, sw, args)                  # initalize a Bag_of_Words CoountVectorizer
        v.corpus = [z.ml_brief[randnb]]         # initalize this BOW with a corpus of TX words
        v.fitandtransform()                     # FIT and TRANSFOR the corpus into a CSR tokenized Term-DOc Matrix

        # test #1
        print ( "---------------------------------- Vectorizer 1 -----------------------------------------" )
        print ( f"ML working on news brief #{randnb}..." )
        print ( f"{z.ml_brief[randnb]}" )
        print ( f"Num of word elements: {v.ft_tdmatrix.nnz}" )
        print ( f"Most common word: {v.get_hfword()}" )
        print ( f"High Frequency word: {v.get_hfword()}" )
        print ( f"Highest count word: {v.ft_tdmatrix.max()}" )
        """
        print ( "----------- Feature names --------------------" )
        print( f"{v.vectorizer.get_feature_names()}" )
        print ( "--------------- Feature counts ---------------" )
        print ( f"{v.ft_tdmatrix}" )
        print ( "---------- Feature word matrix map -----------" )
        v.view_tdmatrix()
        print ( "----------- Vocabulary dictionary ------------" )
        print ( f"{v.vectorizer.vocabulary_}" )
        print ( " " )
        print ( "------------ max word ------------------------" )
        """

        print ( "---------------------------------- Vectorizer 2 -----------------------------------------" )
        randnb2 = random.randint(0, len(z.ml_brief)-1 )
        v.corpus = [z.ml_brief[randnb2]]
        v.fitandtransform()
        print ( f"ML working on news brief #{randnb2}..." )
        print ( f"{z.ml_brief[randnb2]}" )
        print ( f"Num of word elements: {v.ft_tdmatrix.nnz}" )
        print ( f"Most common word: {v.get_hfword()}" )
        print ( f"High Frequency word: {v.get_hfword()}" )
        print ( f"Highest count word: {v.ft_tdmatrix.max()}" )

        """
        print ( f"ML working on news brief #{randnb2}..." )
        print ( f"{z.ml_brief[randnb2]}" )
        print ( f"Most common word: {v.get_hfword()}" )
        print ( "----------- Feature names --------------------" )
        print( f"{v.vectorizer.get_feature_names()}" )
        print ( "--------------- Feature counts ---------------" )
        print ( f"{v.ft_tdmatrix}" )
        print ( "---------- Feature word matrix map -----------" )
        v.view_tdmatrix()
        print ( f"*** High Frequency word: {v.get_hfword()}" )

        print ( "----------- Vocabulary dictionary ------------" )
        print ( f"{v.vectorizer.vocabulary_}" )
        print ( " " )
        print ( "------------ max word ------------------------" )
        print ( f"Num of elements: {v.ft_tdmatrix.nnz}" )
        print ( f"Highest count word: {v.ft_tdmatrix.max()}" )
	"""

    if args['qsymbol'] is not False:
        print ( " " )
        print ( f"Get price action quote for: {args['qsymbol']}" )
        qp = bc_quote(1, args)
        qp.get_basicquote(args['qsymbol'])
        qp.get_quickquote(args['qsymbol'])
        qp.q_polish()
        print ( qp.quote )

        if args['bool_xray'] is True:        # DEBUG Xray
            print ( " " )
            c = 1
            for k, v in qp.quote.items():
                print ( "{:02d} - {}\t\t : {}".format(c, k, v) )
                c += 1

    # print ( " " )
    # qm = mw_quote(1, args)
    # qm.get_quote(args['qsymbol'])

    print ( " " )
    print ( "####### done #####")


if __name__ == '__main__':
    main()
