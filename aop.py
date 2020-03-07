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

# logging setup
logging.basicConfig(level=logging.INFO)

# my private classes & methods
from y_topgainers import y_topgainers
from y_toplosers import y_toplosers
from screener_dg1 import screener_dg1
from unusual_vol import unusual_vol
from shallow_logic import shallow_combo
from y_newsloop import y_newsfilter

# Globals
work_inst = 0
global args
args = {}
global parser
parser = argparse.ArgumentParser(description="Entropy apperture engine")
parser.add_argument('-c','--cycle', help='Ephemerial top 10 every 10 secs for 60 secs', action='store_true', dest='bool_tenten60', required=False, default=False)
parser.add_argument('-d','--deep', help='Deep converged multi data list', action='store_true', dest='bool_deep', required=False, default=False)
parser.add_argument('-n','--newsai', help='News sentiment Ai', action='store_true', dest='bool_news', required=False, default=False)
parser.add_argument('-s','--screen', help='screener logic parser', action='store_true', dest='bool_scr', required=False, default=False)
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

    print ( " " )

    recommended = {}        # dict of recomendations

########### 1 - TOP GAINERS ################
    if args['bool_tops'] is True:
        print ( "========== Top 10 Gainers ==========" )
        med_large_mega_gainers = y_topgainers(1)       # instantiate class
        med_large_mega_gainers.get_topg_data()        # extract data from finance.Yahoo.com
        x = med_large_mega_gainers.build_tg_df0()     # build full dataframe

        print ( " " )
        med_large_mega_gainers.build_top10()           # show top 10
        med_large_mega_gainers.print_top10()           # print it

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
# small caps are isolate outside the regular dataset by yahoo.com
    if args['bool_scr'] is True:
        print ( "========== Screener: SMALL CAP Day Gainers : +5% & > $750M Mkt-cap ==========" )
        small_cap_dataset = screener_dg1(1)       # instantiate class
        small_cap_dataset.get_data()        # extract data from finance.Yahoo.com
        x = small_cap_dataset.build_df0()     # build full dataframe
        # scrn1.build_top10()           # show top 10
        # scrn1.print_top10()           # print it

        # Recommendation #1 - Best small cap % gainer with lowest buy-in price
        recommended.update(small_cap_dataset.screener_logic())
        print ( " ")

########### unusual_vol ################
    if args['bool_uvol'] is True:
        print ( "========== Unusually high Volume ** UP ** =====================================================" )
        un_vol_activity = unusual_vol(1, args)       # instantiate class, args = global var

        un_vol_activity.get_up_unvol_data()        # extract data from finance.Yahoo.com
        uv_up = un_vol_activity.build_df(0)     # build full dataframe

        ulp = un_vol_activity.up_df0['Cur_price'].min()
        uminv = un_vol_activity.up_df0['Cur_price'].idxmin()
        ulsym = un_vol_activity.up_df0.loc[uminv, ['Symbol']][0]
        ulname = un_vol_activity.up_df0.loc[uminv, ['Co_name']][0]

        # Allways make sure this is key #2 in recommendations dict
        recommended['2'] = ('Unusual vol:', ulsym.rstrip(), '$'+str(ulp), ulname.rstrip(), '+%'+str(un_vol_activity.up_df0.loc[uminv, ['Pct_change']][0]) )
        #recommended[uminv] = (ulsym.rstrip(), '$'+str(ulp), ulname.rstrip(), '+%'+str(un_vol_activity.up_df0.loc[uminv, ['Pct_change']][0]) )

        print ( f">>LOWEST<< price OPPTY is: #{uminv} - {ulname.rstrip()} ({ulsym.rstrip()}) @ ${ulp}" )
        print ( " " )
        un_vol_activity.up_unvol_listall()

        print ( " ")
        print ( "========== Unusually high Volume ** DOWN ** =====================================================" )
        un_vol_activity.get_down_unvol_data()
        uv_down = un_vol_activity.build_df(1)     # build full dataframe
        un_vol_activity.down_unvol_listall()
        print ( " ")

########### multi COMBO dataframe query build-out ################
    if args['bool_deep'] is True and args['bool_scr'] is True and args['bool_uvol'] is True:
        # first combine Small_cap + med + large + mega
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
            #recommended[hotidx] = (hotsym.rstrip(), '$'+str(hotp), hotname.rstrip(), '+%'+str(x.combo_df.loc[hotidx, ['Pct_change']][0]) )
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
        #recommended[cminv] = (clsym.rstrip(), '$'+str(clp), clname.rstrip(), '+%'+str(x.combo_df.loc[cminv, ['Pct_change']][0]) )

        # Biggest gainer stock in combo_df
        cmax = x.combo_df['Pct_change'].idxmax()
        clp = x.combo_df.loc[cmax, 'Cur_price']
        clsym = x.combo_df.loc[cmax, ['Symbol']][0]
        clname = x.combo_df.loc[cmax, ['Co_name']][0]

        # allways make sure this is key #5 in recommendations dict
        recommended['5'] = ('Highest % gainer:', clsym.rstrip(), '$'+str(clp), clname.rstrip(), '+%'+str(x.combo_df.loc[cmax, ['Pct_change']][0]) )
        #recommended[cmax] = (clsym.rstrip(), '$'+str(clp), clname.rstrip(), '+%'+str(x.combo_df.loc[cmax, ['Pct_change']][0]) )

        print ( " " )
        print ( f"================= >>LOW<< buy-in recommendations ==================" )
        for k, v in recommended.items():
            print ( f"{k}: {v[0]} {v[1]} {v[2]} {v[3]} {v[4]}" )
            print ( "-------------------------------------------------------------------" )

        print ( " " )
        print ( "============== High level activity inisghts =================" )
        x.combo_grouped()       # insights

    if args['bool_news'] is True:
        print ( " " )
        print ( "========== ** HACKING ** : News Sentiment Ai =======================================" )
        z = y_newsfilter(1, "IBM", args )
        z.scan_news_depth_0()
        if args['bool_deep'] is True:
            ml_prep = z.read_allnews_depth_0()
            # for k, v in ml_prep.items():
                # print ( f"{k}: {v}" )

                # TODO : dump this dict into a Pandas DF and drop+reset the index every time. Add SYMBOL column to DF
                # NOTE: dont iter over dict{} & renumber dict keys. Very bad python form !!
            news_df = pd.DataFrame.from_dict(ml_prep, orient='index', \
                        columns=['Source', 'Outet', 'url_link', 'Author', 'Age'])

            print ( " " )
            print ( news_df )

    print ( "####### done #####")

if __name__ == '__main__':
    main()
