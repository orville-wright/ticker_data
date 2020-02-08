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
        print ( "========== Unusual UP/DOWN Volumes =====================================================" )
        un_vol_activity = unusual_vol(1, args)       # instantiate class, args = global var
        un_vol_activity.get_up_unvol_data()        # extract data from finance.Yahoo.com
        uv_up = un_vol_activity.build_df(0)     # build full dataframe
        un_vol_activity.up_unvol_listall()
        print ( " ")
        un_vol_activity.get_down_unvol_data()
        uv_down = un_vol_activity.build_df(1)     # build full dataframe
        un_vol_activity.down_unvol_listall()
        print ( " ")

########### multi COMBO dataframe query build-out ################
    if args['bool_deep'] is True and args['bool_scr'] is True and args['bool_uvol'] is True:
        # first combine Small_cap + med + large + mega
        deep_1 = med_large_mega_gainers.tg_df1.drop(columns=[ 'ERank', 'Time' ]).sort_values(by='Pct_change', ascending=False )
        deep_2 = small_cap_dataset.dg1_df1.drop(columns=[ 'Row', 'Time' ] )
        deep_3 = un_vol_activity.up_df0.drop(columns=[ 'Row', 'Time', 'Vol', 'Vol_pct']).sort_values(by='Pct_change', ascending=False )
        deep_4 = pd.concat( [ deep_1, deep_2, deep_3], sort=False, ignore_index=True ).sort_values(by=['Pct_change', 'M_B', 'Mkt_cap'], ascending=False, na_position='last')
        deep_4.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        # now scan unusual volume stocks for stock existing in the new combo DataFrame & tage them in a new column

        # print ( "========== Full DEEP combo DataFrame =====================================================" )
        # print ( deep_4 )
        # print ( "========== DEEP combo : duplicates only - style #1 =====================================================" )
        # deep_5 = deep_4.sort_values(by=['Pct_change'], ascending=False )[deep_4.duplicated(['Symbol'])]   # this works **KEEP**
        deep_5 = deep_4.sort_values(by=['Pct_change'], ascending=False )    # prepare a sorted df
        # print ( deep_5[deep_5.duplicated(['Symbol'])] )                     # full dataframe table
        # print ( deep_5[deep_5.duplicated(['Symbol'])].Symbol.values )       # just the symbols as list
        # print ( deep_5[deep_5.duplicated(['Symbol'])].index )               # index ID's as a list

        # print ( "========== DEEP combo : duplicates only - style #2 =====================================================" )
        deep_6 = deep_5.duplicated(['Symbol']).to_frame()      # pd.duplicated outputs a SERIES
        # print ( deep_6[deep_6[0] == True] )        # phase 2 : KEEP

        #deep_5 = deep_4.duplicated(['Symbol']).to_frame()   # pd.duplicated() SERIES result -> DataFrame
        #print ( deep_5[deep_5[0] == True] )                 # select dups - pd.to_frame() default column name = 0

        # scan deep_4 and delete rows with index == deep_6
        print ( "========== DEEP combo no dupes : outlyers described ==========================================" )
        deep_4.drop( deep_6[deep_6[0] == True].index, inplace=True )        # permenantly on the original df
        deep_4 = deep_4.assign(Entropy="" )
        #print ( deep_4 )

        # print ( "========== DEEP combo : Add new column =====================================================" )
        # entropy = {}

        for x in deep_5[deep_5.duplicated(['Symbol'])].Symbol.values:
            row_idx = int(deep_4.loc[deep_4['Symbol'] == x ].index.values)
            cap_size = deep_4.loc[deep_4['Symbol'] == x ].M_B.values
            if cap_size == 'M':
                cap_size = '*Small cap*'
            else:
                cap_size = 'Large cap'
            deep_4.loc[row_idx,'Entropy'] = "Unusual vol "+cap_size

        print ( deep_4 )
        #entropy.update({'*un_vol*': ridx})
        # print ( "Entropy: ", entropy )
        #deep_4.loc[deep_4['Symbol'] == x ]['Entropy'] = "Unusual vol"
        #deep_4['Entropy'] = entropy
        #row = deep_4.loc[deep_4['Symbol'] == x ]
        #print ( "Row: ", row )
        #deep_4['Entropy'] = entropy
        #row = deep_4.insert(rloc, 'Entropy', "Schizzle" )
        #print ( deep_4.loc[deep_4['Symbol'] == x ] )

        # print ( "====================== ALL NaN rows 1 - style 1 =========================" )
        # print ( (deep_4[deep_4['Mkt_cap'].isna()]) )
        # print ( "====================== ALL NaN rows 2 - style 2 =========================" )
        # print ( (deep_4[deep_4['Mkt_cap'].isna()]).iloc[:,[0,5,6]] )    # drop all the known dupes

        # Logic...
        # scan Nan rows DataFrame
        # does each item in duplicates DataFrame exists in NaN DataFrame - !!! also need symbol here
            # YES = guaranteed to have originated from Unusual List table_section
            # NO = bad data0 maybe?
        # on YES...
            # scan full deep combo DataFrame
            # drop row identified dupe row from deep combo DataFrame
            # search deep combo DataFrame (by symbol) of dupe item
                # add column info == "Unusual volume by xxx%"
                # add colum info == "Small, medium. large, mega - cap company"

        """
        index = list(nan_rows['Symbol'])
        for i in index:
            #testdf2['Yearly'][i] = testdf2['Monthly'][i] * testdf2['Tenure'][i]
            print ( "i is:", i )
        """

    print ( "####### done #####")

if __name__ == '__main__':
    main()
