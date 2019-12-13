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
        logging.info('y_topgainers:: - init top_gainers instance: %s' % self )
        # init empty DataFrame with present colum names
        self.tg_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change'] )
        self.tg_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change'] )
        self.tg_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change'] )
        self.yti = yti
        return

# method #1
    def get_topg_data(self):
        """Connect to finance.yahoo.com and extract (scrape) the raw sring data out of"""
        """the Stock:Top Gainers html data table. Returns a BS4 handle."""

        logging.info('y_topgainers::get_topg_data() - In %s' % self.yti )
        with urllib.request.urlopen("https://finance.yahoo.com/gainers/") as url:
            s = url.read()
            logging.info('y_topgainers::get_topg_data() - read html markup stream %s' % self.yti )
            self.soup = BeautifulSoup(s, "html.parser")
        # ATTR style search. Results -> Dict
        # <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
        logging.info('y_topgainers::get_topg_data() - save extracted data -> global attr %s' % self.yti )
        self.all_tag_tr = self.soup.find_all(attrs={"class": "simpTblRow"})

        # target markup line I am scanning looks like this...
        # soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc($extraLightBlue)" )

        # Example CSS Selector
        #all_tag_tr1 = soup.select( "tr.simpTblRow.Bgc" )
        return

# method #2
    def build_tg_df0(self):
        """Build-out a fully populated Pandas DataFrame containg all the"""
        """extracted/scraped fields from the html/markup table data"""
        """Wrangle, clean/convert/format the data correctly."""
        logging.info('y_topgainers::build_tg_df0() - In %s' % self.yti )
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
                       np.float(re.sub('[\+%]', '', pct)) ]]

            self.df0 = pd.DataFrame(self.data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' ], index=[x] )
            self.tg_df0 = self.tg_df0.append(self.df0)    # append this ROW of data into the REAL DataFrame
            x+=1
        logging.info('y_topgainers::build_tg_df0() - Done %s' % self.yti )
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
        logging.info('y_topgainers::topg_listall() - In %s' % self.yti )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.tg_df0.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built
        return

# method #5
    def build_top10(self):
        """Get top 10 gainers from main DF (df0) -> temp DF (df1)"""
        """df1 is ephemerial. Is allways overwritten on each run"""

        logging.info('y_topgainers::build_top10() - In %s' % self )
        logging.info('y_topgainers::build_top10() - Copy top 10 -> Ephemerial DF %s' % self.yti )
        self.tg_df1 = self.tg_df0.sort_values(by='Pct_change', ascending=False ).head(10).copy(deep=True)    # create new DF via copy of top 10 entries
        self.tg_df1.rename(columns = {'Row':'ERank'}, inplace = True)    # Rank is more accurate for this Ephemerial DF
        self.tg_df1.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        return

# method #7
    def print_top10(self):
        """Prints the Top 10 Dataframe"""

        logging.info('y_topgainers::print_top10() - In %s' % self.yti )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.tg_df1.sort_values(by='Pct_change', ascending=False ).head(10) )
        return

# method #6
    def build_tenten60(self):
        """Build the top 10x10x060 historical gainers DataFrame (df2)"""
        """Generally called on some kind of cycle"""

        logging.info('y_topgainers::build_tenten60() - In %s' % self.yti )
        self.tg_df2 = self.tg_df2.append(self.tg_df1, ignore_index=False)    # merge top 10 into
        self.tg_df2.reset_index(inplace=True, drop=True)
        logging.info('y_topgainers::build_tenten60() - Done %s' % self.yti )
        return

#######################################################################
# Global function #1
#
def do_nice_wait(topg_inst):
    """Threaded wait that does work to build out the 10x10x60 DataFrame"""
    logging.info('y_topgainers:: IN Thread - do_nice_wait()' )
    logging.info('y_topgainers::do_nice_wait() -> inst: %s' % topg_inst.yti )
    for r in range(6):
        logging.info('y_topgainers::do_nice_wait() cycle: %s' % topg_inst.cycle )
        time.sleep(5)    # wait immediatley to let remote update
        topg_inst.get_topg_data()        # extract data from finance.Yahoo.com
        topg_inst.build_tg_df0()
        topg_inst.build_top10()
        topg_inst.build_tenten60()
        print ( ".", end="", flush=True )
        topg_inst.cycle += 1    # adv loop cycle

        if topg_inst.cycle == 6:
            logging.info('y_topgainers::do_nice_wait() - EMIT thread exit trigger' )
            extract_done.set()

    logging.info('y_topgainers::do_nice_wait() - Thread cycle: %s' % topg_inst.cycle )
    logging.info('y_topgainers::do_nice_wait() - EXIT thread for inst %s' % topg_inst.yti )

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

# 1st run through
    stg1 = y_topgainers(1)       # instantiate class
    stg1.get_topg_data()        # extract data from finance.Yahoo.com
    x = stg1.build_tg_df0()     # build full dataframe
    print ( "1st run - Extracted", x, "- rows of data from finaince.yahoo.com" )
    print ( " ")
    stg1.build_top10()           # show top 10
    stg1.print_top10()           # print it
    print ( " ")

# **THREAD** waiter
    # do 10x10x60 build-out cycle
    # this will fail to produce a fresh/unique data set as stock_topgainers is loaded via y_topgainers once.
    if args['bool_tenten60'] is True:
        logging.info('y_topgainers:: INIT 10x10x60 main thread cycle' )
        stg3 = y_topgainers(2)
        logging.info('y_topgainers:: START thread -> cycle: %s' % stg3.cycle)
        print ( "Doing 10 sec data extract 6 times: ", end="" )
        thread = threading.Thread(target=do_nice_wait(stg3) )    # thread target passes class instance
        # # WARNING: thread.start() auto called in above setup function...
        # # WARNING: start() exeutes the thread...

        # logging.info('y_topgainers:: START 6x cycler... %s' % stg3.cycle )
        # while not extract_done.wait(timeout=2):     # wait on thread completd trigger
        #    print ( ".", end="", flush=True )

        print ( " " )
        print ( stg3.tg_df2.sort_values(by='Pct_change', ascending=False ) )
    else:
        print ( "##### Not doing 10x10x60 run! #####" )


# 2nd full run to test extraction theory
    print ( "##### Test 2nd run price differnce #####" )
    stg2 = y_topgainers(3)                   # instantiate 2nd unique class
    stg2.get_topg_data()                    # extract data from finance.Yahoo.com
    x2 = stg2.build_tg_df0()                # build full dataframe
    print ( "2nd run - Extracted", x2, "- rows of data from finaince.yahoo.com" )
    # stg2.topg_listall()                     # show full list
    stg2.build_top10()                      # show top 10
    stg2.print_top10()           # print it
    print ( " ")

    print ( "####### done #####")

if __name__ == '__main__':
    main()
