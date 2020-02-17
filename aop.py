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

# Globals
work_inst = 0
global args
args = {}
global parser
parser = argparse.ArgumentParser(description="Entropy apperture engine")
parser.add_argument('-v','--verbose', help='verbose error logging', action='store_true', dest='bool_verbose', required=False, default=False)
parser.add_argument('-c','--cycle', help='Ephemerial top 10 every 10 secs for 60 secs', action='store_true', dest='bool_tenten60', required=False, default=False)
parser.add_argument('-t','--tops', help='show top ganers/losers', action='store_true', dest='bool_tops', required=False, default=False)
parser.add_argument('-s','--screen', help='screener logic parser', action='store_true', dest='bool_scr', required=False, default=False)
parser.add_argument('-u','--unusual', help='unusual up & down volume', action='store_true', dest='bool_uvol', required=False, default=False)
parser.add_argument('-x','--xray', help='dump detailed debug data structures', action='store_true', dest='bool_xray', required=False, default=False)
parser.add_argument('-d','--deep', help='Deep converged multi data list', action='store_true', dest='bool_deep', required=False, default=False)


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

########### 1 - TOP GAINERS ################
    if args['bool_tops'] is True:
        print ( "========== Top 10 Gainers ==========" )
        med_large_mega_gainers = y_topgainers(1)       # instantiate class
        med_large_mega_gainers.get_topg_data()        # extract data from finance.Yahoo.com
        x = med_large_mega_gainers.build_tg_df0()     # build full dataframe
        med_large_mega_gainers.build_top10()           # show top 10
        med_large_mega_gainers.print_top10()           # print it
        print ( " ")

########### 2 - TOP LOSERS ################
    if args['bool_tops'] is True:
        print ( "========== Top 10 Losers ==========" )
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

########### SCREENER 1 ################
    if args['bool_scr'] is True:
        print ( "========== Screener: SMALL CAP Day Gainers : +5% & > $750M Mkt-cap ==========" )
        small_cap_dataset = screener_dg1(1)       # instantiate class
        small_cap_dataset.get_data()        # extract data from finance.Yahoo.com
        x = small_cap_dataset.build_df0()     # build full dataframe
        # scrn1.build_top10()           # show top 10
        # scrn1.print_top10()           # print it
        small_cap_dataset.screener_logic()
        print ( " ")

########### unusual_vol ################
    if args['bool_uvol'] is True:
        print ( "========== Unusually high Volume ** UP ** =====================================================" )
        un_vol_activity = unusual_vol(1, args)       # instantiate class, args = global var
        un_vol_activity.get_up_unvol_data()        # extract data from finance.Yahoo.com
        uv_up = un_vol_activity.build_df(0)     # build full dataframe
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
        print ( "========== ** OUTLIERS ** : with Annotated reasons =======================================" )
        x.tag_dupes()
        x.tag_uniques()
        # print ( "========== ** Hacking *** : prepare Ranking =======================================" )
        # x.rank_hot()
        x.rank_hot()
        print ( x.combo_listall() )

    print ( "####### done #####")

if __name__ == '__main__':
    main()
