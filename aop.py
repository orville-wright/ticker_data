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
work_inst = 0

# Threading globals
extract_done = threading.Event()
yti = 1

class y_topgainers:
    """Class to extract Top Gainer data set from finance.yahoo.com"""

    # global accessors
    tg_df0 = ""          # DataFrame - Full list of top gainers
    tg_df1 = ""          # DataFrame - Ephemerial list of top 10 gainers. Allways overwritten
    tg_df2 = ""          # DataFrame - Top 10 ever 10 secs for 60 secs
    all_tag_tr = ""      # BS4 handle of the <tr> extracted data
    yti = 0
    cycle = 0           # class thread loop counter

    def __init__(self, yti):
        logging.info('y_topgainers:: INIT inst: %s' % self )
        logging.info('y_topgainers:: Inst #: %s' % yti )    # catches 1st instantiate 0|1
        # init empty DataFrame with present colum names
        self.tg_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Time'] )
        self.tg_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Time'] )
        self.tg_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Time'] )
        self.yti = yti
        return

# method #1
    def get_topg_data(self):
        """Connect to finance.yahoo.com and extract (scrape) the raw sring data out of"""
        """the embedded webpage [Stock:Top Gainers] html data table. Returns a BS4 handle."""

        logging.info('ins.#%s.get_topg_data() - IN' % self.yti )
        with urllib.request.urlopen("https://finance.yahoo.com/gainers/" ) as url:
            s = url.read()
            logging.info('ins.#%s.get_topg_data() - read html stream' % self.yti )
            self.soup = BeautifulSoup(s, "html.parser")
        # ATTR style search. Results -> Dict
        # <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
        logging.info('ins.#%s.get_topg_data() - save data handle' % self.yti )
        self.all_tag_tr = self.soup.find_all(attrs={"class": "simpTblRow"})

        # target markup line I am scanning looks like this...
        # soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc($extraLightBlue)" )

        # Example CSS Selector
        #all_tag_tr1 = soup.select( "tr.simpTblRow.Bgc" )
        logging.info('ins.#%s.get_topg_data() - close url handle' % self.yti )
        url.close()
        return

# method #2
    def build_tg_df0(self):
        """Build-out a fully populated Pandas DataFrame containg all the"""
        """extracted/scraped fields from the html/markup table data"""
        """Wrangle, clean/convert/format the data correctly."""
        logging.info('ins.#%s.build_tg_df0() - IN' % self.yti )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('ins.#%s.build_tg_df0() - Drop all rows from DF0' % self.yti )
        self.tg_df0.drop(self.tg_df0.index, inplace=True)
        x = 1    # row counter Also leveraged for unique dataframe key
        for datarow in self.all_tag_tr:
            # 1st <td> cell : ticker symbol info & has comment of company name
            # 2nd <td> cell : company name
            # 3rd <td> cell : price
            # 4th <td> cell : $ change
            # 5th <td> cell : % change
            # more cells in <tr> data row...but I'm not interested in them at moment.

            # BS4 generator object comes from "extracted strings" BS4 operation (nice)
            extr_strings = datarow.stripped_strings
            co_sym = next(extr_strings)
            co_name = next(extr_strings)
            price = next(extr_strings)
            change = next(extr_strings)
            pct = next(extr_strings)

            co_sym_lj = np.char.ljust(co_sym, 6)       # use numpy to left justify TXT in pandas DF
            co_name_lj = np.char.ljust(co_name, 20)    # use numpy to left justify TXT in pandas DF

            # note: Pandas DataFrame : top_gainers pre-initalized as EMPYT
            # Data treatment:
            # Data is extracted as raw strings, so needs wrangeling...
            #    price - stip out any thousand "," seperators and cast as true decimal via numpy
            #    change - strip out chars '+' and ',' and cast as true decimal via numpy
            #    pct - strip out chars '+ and %' and cast as true decimal via numpy
            self.data0 = [[ \
                       x, \
                       co_sym_lj, \
                       co_name_lj, \
                       np.float(re.sub('\,', '', price)), \
                       np.float(re.sub('[\+,]', '', change)), \
                       np.float(re.sub('[\+%]', '', pct)), \
                       time_now ]]

            self.df0 = pd.DataFrame(self.data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Time' ], index=[x] )
            self.tg_df0 = self.tg_df0.append(self.df0)    # append this ROW of data into the REAL DataFrame
            x+=1
        logging.info('ins.#%s.build_tg_df0() - populated new DF0 dataset' % self.yti )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)
                        # sucess = lobal class accessor (y_topgainers.tg_df0) populated & updated

# method #3
# Hacking function - keep me arround for a while
    def prog_bar(self, x, y):
        """simple progress dialogue function"""
        if x % y == 0:
            print ( " " )
        else:
            print ( ".", end="" )
        return

# method #4
    def topg_listall(self):
        """Print the full DataFrame table list of Yahoo Finance Top Gainers"""
        """Sorted by % Change"""
        # stock_topgainers = get_topgainers()
        logging.info('ins.#%s.topg_listall() - IN' % self.yti )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.tg_df0.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built
        return

# method #5
    def build_top10(self):
        """Get top 10 gainers from main DF (df0) -> temp DF (df1)"""
        """df1 is ephemerial. Is allways overwritten on each run"""

        logging.info('ins.#%s.build_top10() - IN' % self.yti )
        logging.info('ins.#%s.build_top10() - Drop all rows from DF1' % self.yti )
        self.tg_df1.drop(self.tg_df1.index, inplace=True)
        logging.info('ins.#%s.build_top10() - Copy DF0 -> ephemerial DF1' % self.yti )
        self.tg_df1 = self.tg_df0.sort_values(by='Pct_change', ascending=False ).head(10).copy(deep=True)    # create new DF via copy of top 10 entries
        self.tg_df1.rename(columns = {'Row':'ERank'}, inplace = True)    # Rank is more accurate for this Ephemerial DF
        self.tg_df1.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        return

# method #7
    def print_top10(self):
        """Prints the Top 10 Dataframe"""

        logging.info('ins.#%s.print_top10() - IN' % self.yti )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.tg_df1.sort_values(by='Pct_change', ascending=False ).head(10) )
        return

# method #6
    def build_tenten60(self, cycle):
        """Build-up 10x10x060 historical DataFrame (df2) from source df1"""
        """Generally called on some kind of cycle"""

        logging.info('ins.#%s.build_tenten60() - IN' % self.yti )
        self.tg_df2 = self.tg_df2.append(self.tg_df1, ignore_index=False)    # merge top 10 into
        self.tg_df2.reset_index(inplace=True, drop=True)    # ensure index is allways unique + sequential
        return

#######################################################################
# Global thread function #1
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

############# Test

def bkgrnd_worker():
    """Threaded wait that does work to build out the 10x10x60 DataFrame"""
    global work_inst
    logging.info('bkgrnd_worker() IN Thread - bkgrnd_worker()' )
    logging.info('bkgrnd_worker() Ref -> inst #: %s' % work_inst.yti )
    for r in range(6):
        logging.info('bkgrnd_worker():: Loop: %s' % r )
        time.sleep(10)    # wait immediatley to let remote update
        work_inst.get_topg_data()        # extract data from finance.Yahoo.com
        work_inst.build_tg_df0()
        work_inst.build_top10()
        work_inst.build_tenten60(r)

    logging.info('bkgrnd_worker() EMIT exit trigger' )
    extract_done.set()
    logging.info('bkgrnd_worker() EXIT thread inst #: %s' % work_inst.yti )
    return      # dont know if this this requireed or good semantics?

#######################################################################
# TODO: methods/Functions to add...
#       see README and TODO.txt

############################# main() ##################################
#
def main():
    # setup valid cmdline args
    parser = argparse.ArgumentParser()
    parser.add_argument('-v','--verbose', help='verbose error logging', action='store_true', dest='bool_verbose', required=False, default=False)
    parser.add_argument('-s','--sixty', help='Ephemerial top 10 every 10 secs for 60 secs', action='store_true', dest='bool_tenten60', required=False, default=False)

    args = vars(parser.parse_args())
    print ( " " )
    print ( "########## Initalizing ##########" )
    print ( " " )

    # ARGS[] cmdline pre-processing
    if args['bool_verbose'] is True:        # Logging level
        print ( "Enabeling verbose info logging..." )
        logging.disable(0)                  # Log level = OFF
    else:
        logging.disable(20)                 # Log lvel = INFO

    print ( "Command line args..." )
    print ( parser.parse_args() )
    print ( " " )

########### 1 ################
# 1st run through
    stg1 = y_topgainers(1)       # instantiate class
    stg1.get_topg_data()        # extract data from finance.Yahoo.com
    x = stg1.build_tg_df0()     # build full dataframe
    print ( "1st run - Extracted", x, "- rows of data from finaince.yahoo.com" )
    print ( " ")
    stg1.build_top10()           # show top 10
    stg1.print_top10()           # print it
    print ( " ")

########### 2 ################
# **THREAD** waiter
    # do 10x10x60 build-out cycle
    # currently fails to produce a unique data set each threat cycle. Don't know why
    if args['bool_tenten60'] is True:
        print ( "Doing 10x10x60 cycle" )
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
        print ( work_inst.tg_df2.sort_values(by=['Symbol','Time'], ascending=True ) )
    else:
        print ( "##### Not doing 10x10x60 run! #####" )

    print ( "####### done #####")

if __name__ == '__main__':
    main()
