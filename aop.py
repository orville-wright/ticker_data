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
wait_trigger = threading.Event()

class y_topgainers:
    """Class to extract Top Gainer data set from finance.yahoo.com"""

    # global accessors
    tg_df0 = ""          # DataFrame - Full list of top gainers
    tg_df1 = ""          # DataFrame - Ephemerial list of top 10 gainers. Allways overwritten
    tg_df2 = ""          # DataFrame - Top 10 ever 10 secs for 60 secs
    all_tag_tr = ""      # BS4 handle of the <tr> extracted data

    def __init__(self):
        logging.info('y_topgainers:: - init top_gainers instance' )
        # init empty DataFrame with present colum names
        y_topgainers.tg_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change'] )
        y_topgainers.tg_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change'] )
        y_topgainers.tg_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change'] )
        return

# method #1
    def get_topg_data(self):
        """Connect to finance.yahoo.com and extract (scrape) the raw sring data out of"""
        """the Stock:Top Gainers html data table. Returns a BS4 handle."""

        logging.info('y_topgainers::get_topg_data() - In' )
        with urllib.request.urlopen("https://finance.yahoo.com/gainers/") as url:
            s = url.read()
            logging.info('y_topgainers::get_topg_data() - read html markup stream' )
            soup = BeautifulSoup(s, "html.parser")
        # ATTR style search. Results -> Dict
        # <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
        logging.info('y_topgainers::get_topg_data() - save extracted data -> global attr' )
        y_topgainers.all_tag_tr = soup.find_all(attrs={"class": "simpTblRow"})

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
        logging.info('y_topgainers::build_tg_df0() - In' )
        x = 1    # row counter Also leveraged for unique dataframe key
        for datarow in y_topgainers.all_tag_tr:
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
            data0 = [[ \
                       x, \
                       co_sym_lj, \
                       co_name_lj, \
                       np.float(re.sub('\,', '', price)), \
                       np.float(re.sub('[\+,]', '', change)), \
                       np.float(re.sub('[\+%]', '', pct)) ]]

            df0 = pd.DataFrame(data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' ], index=[x] )
            y_topgainers.tg_df0 = y_topgainers.tg_df0.append(df0)    # append this ROW of data into the REAL DataFrame
            x+=1
        logging.info('y_topgainers::build_tg_df0() - Done' )
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
        logging.info('y_topgainers::topg_listall() - In' )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( y_topgainers.tg_df0.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built
        return

# method #5
    def build_top10(self):
        """Print the top 10 gainers only and store table in Ephemerial DataFrame"""
        """The Ephemerial DF is allway overwritten every time this method runs"""
        logging.info('y_topgainers::build_top10() - In' )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        logging.info('y_topgainers::build_top10() - Copy top 10 -> Ephemerial DF' )
        y_topgainers.tg_df1 = y_topgainers.tg_df0.sort_values(by='Pct_change', ascending=False ).head(10).copy(deep=True)    # create new DF via copy
        y_topgainers.tg_df1.rename(columns = {'Row':'ERank'}, inplace = True)    # Rank is more accurate for this Ephemerial DF
        y_topgainers.tg_df1.reset_index(inplace=True, drop=True)
        # print ( y_topgainers.tg_df1.sort_values(by='Pct_change', ascending=False ).head(10) )
        return

# method #6
    def build_tenten60(self):
        """Build the top 10x10x060 Ephemerial rankig gainers DataFrame"""
        """10x10x60 analysis is top 10 gaines every 10 seconds for 60 seconds"""

        logging.info('y_topgainers::build_tenten60() - In' )
        x = 1    # row counter Also leveraged for unique dataframe key
        y_topgainers.tg_df2 = y_topgainers.tg_df2.append(y_topgainers.tg_df1, ignore_index=False)    # merge top 10 into
        y_topgainers.tg_df2.reset_index(inplace=True, drop=True)
        x+=1
        logging.info('y_topgainers::build_tenten60() - Done' )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)

# Global function #1
#
def do_nice_wait(topg_inst):
    """Threaded wait that does work to build out the 10x10x60 DataFrame"""
    logging.info('y_topgainers::do_nice_wait() - In' )

    for x in range(1, 6):    # loop 6 x, wait 10 sec, for a total of 60 seconds
        print ( "Build 10x10x60 -> cycle: ", x )
        topg_inst.build_tg_df0()
        topg_inst.build_top10()
        topg_inst.build_tenten60()
        time.sleep(10)    # testing wait time = 5 secs

    logging.info('y_topgainers::do_nice_wait() - emitting thread exit trigger' )
    wait_trigger.set()
    logging.info('y_topgainers::do_nice_wait() - Thread exit' )
    return      # dont know if this this requireed or good semantics?

#######################################################################
# TODO: methods/Functions to add...
#       see README and TODO.txt

############################# main() ##################################
#
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v','--verbose', help='verbose error logging', action='store_true', dest='bool_verbose', required=False, default=False)
    parser.add_argument('-s','--sixty', help='Ephemerial top 10 every 10 secs for 60 secs', action='store_true', dest='bool_tenten60', required=False, default=False)

    args = vars(parser.parse_args())
    print ( " " )
    print ( "########## Initalizing ##########" )
    print ( " " )

    # ARGS[] pre-processing - set-ip logging before anything else
    if args['bool_verbose'] is True:
        print ( "Enabeling verbose info logging..." )
        logging.disable(0)     # Log level = NOTSET
    else:
        logging.disable(20)    # Log lvel = INFO

    print ( "Command line args..." )
    print ( parser.parse_args() )
    print ( " " )

    stock_topgainers = y_topgainers()       # instantiate class
    stock_topgainers.get_topg_data()        # extract data from finance.Yahoo.com
    x = stock_topgainers.build_tg_df0()     # build full dataframe
    print ( "Extracted", x, "- rows of data from finaince.yahoo.com" )
    stock_topgainers.topg_listall()         # show full list
    print ( " ")
    stock_topgainers.build_top10()           # show top 10
    print ( stock_topgainers.tg_df1.sort_values(by='Pct_change', ascending=False ).head(10) )
    print ( " ")

    # Threaded wait looper...
    thread = threading.Thread(target=do_nice_wait(stock_topgainers) )    # thread target passes class instance
    thread.start()         # initialize thread
    wait_trigger.wait()    # wait here for the trigger to be available before continuing

    print ( stock_topgainers.tg_df2.sort_values(by='Pct_change', ascending=False ) )
    print ( "####### done #####")

if __name__ == '__main__':
    main()
